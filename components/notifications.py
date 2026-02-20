import streamlit as st
from database import get_db
from models import Alert
from datetime import datetime

def render_notifications():
    """Render notification center in sidebar"""
    if not st.session_state.get('authenticated', False):
        return
    
    # Auto-refresh every 5 seconds to check for new notifications
    st.markdown("""
    <script>
        // Auto-refresh page every 5 seconds to get new notifications
        setTimeout(function(){
            window.parent.location.reload();
        }, 5000); // 5 seconds
    </script>
    """, unsafe_allow_html=True)
    
    user_id = st.session_state.user.id
    db = get_db()
    
    try:
        # Get unread notifications count
        unread_count = db.query(Alert).filter(
            Alert.user_id == user_id,
            Alert.read == False
        ).count()
        
        # Display notification bell with badge
        st.sidebar.markdown("---")
        
        # Add refresh button and notification header
        col1, col2 = st.sidebar.columns([3, 1])
        with col1:
            if unread_count > 0:
                st.markdown(f"### 🔔 Notifications ({unread_count})")
            else:
                st.markdown("### 🔔 Notifications")
        with col2:
            if st.button("🔄", key="refresh_notifications", help="Refresh notifications"):
                st.rerun()
        
        # Get recent notifications (last 10)
        notifications = db.query(Alert).filter(
            Alert.user_id == user_id
        ).order_by(Alert.created_at.desc()).limit(10).all()
        
        if notifications:
            for notif in notifications:
                severity_emoji = {
                    'high': '🔴',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(notif.severity, '🔵')
                
                # Different styling for read/unread
                if notif.read:
                    st.sidebar.markdown(f"""
                    <div style="
                        padding: 10px;
                        margin: 5px 0;
                        border-radius: 8px;
                        background-color: #f0f0f0;
                        border-left: 3px solid #ccc;
                        opacity: 0.6;
                    ">
                        <small>{severity_emoji} {notif.type.replace('_', ' ').title()}</small><br>
                        <small>{notif.message}</small><br>
                        <small style="color: #999;">{notif.created_at.strftime('%b %d, %I:%M %p')}</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.sidebar.markdown(f"""
                    <div style="
                        padding: 10px;
                        margin: 5px 0;
                        border-radius: 8px;
                        background-color: #E8F5E9;
                        border-left: 3px solid #4CAF50;
                        font-weight: 500;
                    ">
                        <small>{severity_emoji} <b>{notif.type.replace('_', ' ').title()}</b></small><br>
                        <small>{notif.message}</small><br>
                        <small style="color: #2E7D32;">{notif.created_at.strftime('%b %d, %I:%M %p')}</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Mark all as read button
            if unread_count > 0:
                if st.sidebar.button("✓ Mark All as Read", key="mark_all_read"):
                    db.query(Alert).filter(
                        Alert.user_id == user_id,
                        Alert.read == False
                    ).update({"read": True})
                    db.commit()
                    st.rerun()
        else:
            st.sidebar.info("No notifications yet")
            
    finally:
        db.close()


def create_notification(user_id: int, notif_type: str, message: str, severity: str = "low", barn_id: int = None):
    """Helper function to create a notification"""
    db = get_db()
    try:
        alert = Alert(
            type=notif_type,
            message=message,
            severity=severity,
            barn_id=barn_id,
            user_id=user_id,
            read=False,
            created_at=datetime.utcnow()
        )
        db.add(alert)
        db.commit()
    finally:
        db.close()


def notify_users_on_checklist(checklist, submitter_name):
    """Send notifications to admins and managers when checklist is submitted"""
    from models import User
    db = get_db()
    try:
        # Get all admins and managers
        notification_users = db.query(User).filter(
            User.role.in_(['admin', 'manager']),
            User.is_active == True
        ).all()
        
        barn_name = checklist.barn.name if checklist.barn else "Unknown Barn"
        
        for user in notification_users:
            create_notification(
                user_id=user.id,
                notif_type="checklist_submitted",
                message=f"New checklist submitted by {submitter_name} for {barn_name} - ⏳ PENDING REVIEW",
                severity="low",
                barn_id=checklist.barn_id
            )
    finally:
        db.close()


def notify_users_on_incident(incident, submitter_name):
    """Send notifications to admins, managers, and vets when incident is reported"""
    from models import User
    db = get_db()
    try:
        # Determine who to notify based on severity
        notification_roles = ['admin', 'manager']
        if incident.severity == 'high' or incident.incident_type == 'disease':
            notification_roles.append('vet')
        
        notification_users = db.query(User).filter(
            User.role.in_(notification_roles),
            User.is_active == True
        ).all()
        
        barn_name = incident.barn.name if incident.barn else "Unknown Barn"
        
        for user in notification_users:
            create_notification(
                user_id=user.id,
                notif_type="incident_reported",
                message=f"🚨 {incident.severity.upper()} incident reported by {submitter_name} at {barn_name}: {incident.incident_type} - ⚠️ PENDING APPROVAL",
                severity=incident.severity,
                barn_id=incident.barn_id
            )
    finally:
        db.close()


def notify_worker_on_checklist_approval(checklist, approver_name):
    """Notify worker when their checklist is approved"""
    barn_name = checklist.barn.name if checklist.barn else "Unknown Barn"
    create_notification(
        user_id=checklist.user_id,
        notif_type="checklist_approved",
        message=f"✅ Your checklist for {barn_name} has been approved by {approver_name}",
        severity="low",
        barn_id=checklist.barn_id
    )


def notify_worker_on_incident_approval(incident, approver_name):
    """Notify worker when their incident is approved"""
    barn_name = incident.barn.name if incident.barn else "Unknown Barn"
    create_notification(
        user_id=incident.user_id,
        notif_type="incident_approved",
        message=f"✅ Your {incident.severity} severity incident at {barn_name} has been approved by {approver_name}",
        severity="low",
        barn_id=incident.barn_id
    )
