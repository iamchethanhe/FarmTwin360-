import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database import get_db, get_accessible_farm_ids
from models import Barn, Checklist, Incident, Alert, Farm, User
from utils import get_dashboard_metrics, display_alerts_sidebar, get_risk_color
from components.visualization import render_3d_farm
from translations import get_text
from ai_engine import risk_predictor

def render_admin_dashboard():
    """Admin dashboard - Full system overview"""
    display_alerts_sidebar()
    
    st.markdown("### 👑 Admin Dashboard - Full Farm System Overview")
    
    db = get_db()
    try:
        # Get all metrics
        metrics = get_dashboard_metrics()
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label=get_text("total_barns"),
                value=metrics["total_barns"]
            )
        
        with col2:
            st.metric(
                label=get_text("high_risk_barns"),
                value=metrics["high_risk_barns"],
                delta=f"{metrics['high_risk_barns']}/{metrics['total_barns']}"
            )
        
        with col3:
            st.metric(
                label=get_text("total_checklists"),
                value=metrics["total_checklists"]
            )
        
        with col4:
            st.metric(
                label=get_text("unresolved_incidents"),
                value=metrics["unresolved_incidents"]
            )
        
        # Admin-specific content
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(get_text("farm_visualization"))
            render_3d_farm()
        
        with col2:
            st.subheader(get_text("recent_activities"))
            render_recent_activities()
        
        # Charts row
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(get_text("risk_distribution"))
            render_risk_distribution_chart()
        
        with col2:
            st.subheader(get_text("checklist_trends"))
            render_checklist_trends()
        
        # Admin Quick Actions
        st.divider()
        st.subheader("⚙️ Quick Admin Actions")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("👥 Manage Users", use_container_width=True, key="admin_users"):
                st.session_state.admin_quick_action = "users"
                st.rerun()
        
        with col2:
            if st.button("🏠 Manage Farms", use_container_width=True, key="admin_farms"):
                st.session_state.admin_quick_action = "farms"
                st.rerun()
        
        with col3:
            if st.button("🔗 Farm Assignments", use_container_width=True, key="admin_assign"):
                st.session_state.admin_quick_action = "assignments"
                st.rerun()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🏭 Manage Barns", use_container_width=True, key="admin_barns"):
                st.session_state.admin_quick_action = "barns"
                st.rerun()
        
        with col2:
            if st.button("⚙️ System Settings", use_container_width=True, key="admin_settings"):
                st.session_state.admin_quick_action = "settings"
                st.rerun()
        
        with col3:
            if st.button("🔄 Update AI Predictions", use_container_width=True, key="admin_ai"):
                with st.spinner(get_text("updating_predictions")):
                    success = risk_predictor.update_barn_risks()
                    if success:
                        st.success(get_text("predictions_updated"))
                        st.rerun()
                    else:
                        st.error(get_text("predictions_error"))
        
        # Handle admin quick actions
        if st.session_state.get('admin_quick_action'):
            action = st.session_state.admin_quick_action
            st.session_state.admin_quick_action = None  # Reset
            
            if action == "users":
                st.session_state.show_admin_section = "users"
            elif action == "farms":
                st.session_state.show_admin_section = "farms"
            elif action == "assignments":
                st.session_state.show_admin_section = "assignments"
            elif action == "barns":
                st.session_state.show_admin_section = "barns"
            elif action == "settings":
                st.session_state.show_admin_section = "settings"
        
        # System statistics
        st.divider()
        st.subheader("📊 System Statistics")
        
        user_count = db.query(User).count()
        farm_count = db.query(Farm).count()
        barn_count = db.query(Barn).count()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Users", user_count)
        with col2:
            st.metric("Total Farms", farm_count)
        with col3:
            st.metric("Total Barns", barn_count)
    
    finally:
        db.close()

def render_manager_dashboard():
    """Manager dashboard - Farm and approval management"""
    display_alerts_sidebar()
    
    st.markdown("### 👔 Manager Dashboard - Farm Operations & Approvals")
    
    db = get_db()
    try:
        user_id = st.session_state.get('user').id
        user_role = st.session_state.get('role')
        accessible_farm_ids = get_accessible_farm_ids(user_id, user_role, db)
        
        if not accessible_farm_ids:
            st.warning("No farms assigned to you. Please contact admin.")
            return
        
        # Get metrics for assigned farms
        barns = db.query(Barn).filter(Barn.farm_id.in_(accessible_farm_ids)).all()
        barn_ids = [b.id for b in barns]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Assigned Barns", len(barns))
        
        with col2:
            high_risk = len([b for b in barns if b.risk_level == "high"])
            st.metric("High Risk Barns", high_risk)
        
        with col3:
            pending_checklists = db.query(Checklist).filter(
                Checklist.barn_id.in_(barn_ids),
                Checklist.approved == False
            ).count()
            st.metric("Pending Checklists", pending_checklists)
        
        with col4:
            pending_incidents = db.query(Incident).filter(
                Incident.barn_id.in_(barn_ids),
                Incident.approved == False
            ).count()
            st.metric("Pending Incidents", pending_incidents)
        
        # Main content
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Farm Visualization")
            render_3d_farm()
        
        with col2:
            st.subheader(get_text("recent_activities"))
            render_recent_activities()
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(get_text("risk_distribution"))
            render_risk_distribution_chart()
        
        with col2:
            st.subheader(get_text("checklist_trends"))
            render_checklist_trends()
        
        # Manager Quick Actions
        st.divider()
        st.subheader("📌 Manager Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📋 Review Checklists", use_container_width=True, key="mgr_checklists"):
                st.session_state.manager_quick_action = "checklists"
                st.rerun()
        
        with col2:
            if st.button("⚠️ Review Incidents", use_container_width=True, key="mgr_incidents"):
                st.session_state.manager_quick_action = "incidents"
                st.rerun()
        
        with col3:
            if st.button("🔄 Update Risk Predictions", use_container_width=True, key="mgr_ai"):
                with st.spinner("Updating predictions..."):
                    success = risk_predictor.update_barn_risks()
                    if success:
                        st.success("Predictions updated successfully")
                        st.rerun()
                    else:
                        st.error("Error updating predictions")
        
        # Handle manager quick actions
        if st.session_state.get('manager_quick_action'):
            action = st.session_state.manager_quick_action
            st.session_state.manager_quick_action = None  # Reset
            
            if action == "checklists":
                st.session_state.show_manager_approvals = "checklists"
            elif action == "incidents":
                st.session_state.show_manager_approvals = "incidents"
    
    finally:
        db.close()

def render_worker_dashboard():
    """Worker dashboard - Task-focused view"""
    display_alerts_sidebar()
    
    st.markdown("### 👷 Worker Dashboard - My Tasks & Submissions")
    
    db = get_db()
    try:
        user_id = st.session_state.get('user').id
        user_role = st.session_state.get('role')
        accessible_farm_ids = get_accessible_farm_ids(user_id, user_role, db)
        
        if not accessible_farm_ids:
            st.warning("No farms assigned to you. Please contact admin.")
            return
        
        # Worker metrics
        my_checklists = db.query(Checklist).filter(
            Checklist.user_id == user_id
        ).count()
        
        my_incidents = db.query(Incident).filter(
            Incident.user_id == user_id
        ).count()
        
        pending_approvals = db.query(Checklist).filter(
            Checklist.user_id == user_id,
            Checklist.approved == False
        ).count() + db.query(Incident).filter(
            Incident.user_id == user_id,
            Incident.approved == False
        ).count()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("My Checklists", my_checklists)
        
        with col2:
            st.metric("My Incidents", my_incidents)
        
        with col3:
            st.metric("Pending Approval", pending_approvals)
        
        with col4:
            assigned_barns = len(db.query(Barn).filter(
                Barn.farm_id.in_(accessible_farm_ids)
            ).all())
            st.metric("My Assigned Barns", assigned_barns)
        
        # Quick action buttons
        st.subheader("📋 Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📝 Submit New Checklist", use_container_width=True):
                st.info("Use the 'Worker Interface' from the sidebar to submit checklists.")
        
        with col2:
            if st.button("🚨 Report Incident", use_container_width=True):
                st.info("Use the 'Worker Interface' from the sidebar to report incidents.")
        
        with col3:
            if st.button("📊 View My Submissions", use_container_width=True):
                st.info("Check the 'My Submissions' tab in the 'Worker Interface' section.")
        
        # My recent submissions
        st.divider()
        st.subheader("📌 My Recent Submissions")
        
        recent_checklists = db.query(Checklist).filter(
            Checklist.user_id == user_id
        ).order_by(Checklist.submitted_at.desc()).limit(3).all()
        
        recent_incidents = db.query(Incident).filter(
            Incident.user_id == user_id
        ).order_by(Incident.reported_at.desc()).limit(3).all()
        
        if recent_checklists:
            st.write("**Recent Checklists:**")
            for c in recent_checklists:
                status = "✅ Approved" if c.approved else "⏳ Pending"
                st.write(f"• {c.barn.name if c.barn else 'N/A'} - {status} ({c.submitted_at.strftime('%Y-%m-%d')})") 
        
        if recent_incidents:
            st.write("**Recent Incidents:**")
            for inc in recent_incidents:
                status = "✅ Approved" if inc.approved else "⏳ Pending"
                severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(inc.severity, "⚪")
                st.write(f"• {severity_icon} {inc.barn.name if inc.barn else 'N/A'} - {status} ({inc.reported_at.strftime('%Y-%m-%d')})") 
    
    finally:
        db.close()

def render_vet_dashboard():
    """Vet dashboard - Health and disease monitoring"""
    display_alerts_sidebar()
    
    st.markdown("### 🩺 Veterinarian Dashboard - Health Monitoring")
    
    db = get_db()
    try:
        user_id = st.session_state.get('user').id
        user_role = st.session_state.get('role')
        accessible_farm_ids = get_accessible_farm_ids(user_id, user_role, db)
        
        if not accessible_farm_ids:
            st.warning("No farms assigned to you. Please contact admin.")
            return
        
        # Get barns from assigned farms
        barns = db.query(Barn).filter(Barn.farm_id.in_(accessible_farm_ids)).all()
        barn_ids = [b.id for b in barns]
        
        # Vet-specific metrics
        disease_incidents = db.query(Incident).filter(
            Incident.barn_id.in_(barn_ids),
            Incident.incident_type == 'disease',
            Incident.approved == True
        ).count()
        
        high_severity_incidents = db.query(Incident).filter(
            Incident.barn_id.in_(barn_ids),
            Incident.severity == 'high',
            Incident.approved == True
        ).count()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Disease Cases", disease_incidents)
        
        with col2:
            st.metric("High Severity Cases", high_severity_incidents)
        
        with col3:
            st.metric("Monitored Barns", len(barns))
        
        with col4:
            st.metric("Assigned Farms", len(accessible_farm_ids))
        
        # Main content
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Farm Overview")
            render_3d_farm()
        
        with col2:
            st.subheader("Recent Activities")
            render_recent_activities()
        
        # Disease incidents report
        st.divider()
        st.subheader("🏥 Disease & Health Incidents")
        
        disease_data = []
        for inc in db.query(Incident).filter(
            Incident.barn_id.in_(barn_ids),
            Incident.approved == True
        ).order_by(Incident.reported_at.desc()).limit(10).all():
            if inc.incident_type == 'disease' or inc.severity == 'high':
                disease_data.append({
                    "Date": inc.reported_at.strftime("%Y-%m-%d %H:%M"),
                    "Barn": inc.barn.name if inc.barn else "N/A",
                    "Type": inc.incident_type.replace('_', ' ').title(),
                    "Severity": inc.severity.upper(),
                    "Resolved": "✅" if inc.resolved else "⏳"
                })
        
        if disease_data:
            df = pd.DataFrame(disease_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No disease or high-severity incidents reported.")
    
    finally:
        db.close()

def render_auditor_dashboard():
    """Auditor dashboard - System-wide audit view"""
    display_alerts_sidebar()
    
    st.markdown("### 📊 Auditor Dashboard - System-wide Audit View")
    
    # Auditors see all farms
    metrics = get_dashboard_metrics()
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Barns", metrics["total_barns"])
    
    with col2:
        st.metric("High Risk Barns", metrics["high_risk_barns"])
    
    with col3:
        st.metric("Total Checklists", metrics["total_checklists"])
    
    with col4:
        st.metric("Unresolved Incidents", metrics["unresolved_incidents"])
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(get_text("farm_visualization"))
        render_3d_farm()
    
    with col2:
        st.subheader(get_text("recent_activities"))
        render_recent_activities()
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(get_text("risk_distribution"))
        render_risk_distribution_chart()
    
    with col2:
        st.subheader(get_text("checklist_trends"))
        render_checklist_trends()
    
    # Audit-specific content
    st.divider()
    st.subheader("🔍 Audit Information")
    
    st.info("✓ As an Auditor, you have read-only access to all farms and data for audit purposes.")

def render_visitor_dashboard():
    """Visitor dashboard - Limited access view"""
    st.markdown("### 👤 Welcome, Visitor")
    
    st.info("You have limited access as a visitor. Your dashboard shows your check-in status.")
    
    db = get_db()
    try:
        # Get recent visitor records for current user (if logged in)
        st.subheader("Your Recent Visits")
        st.write("Please check your visit history in the 'Visitor Check-In' section from the sidebar.")
    finally:
        db.close()

def render_default_dashboard():
    """Default dashboard for unknown roles"""
    st.warning("Your role could not be determined. Please contact administrator.")

# Import these functions from the main dashboard module
def render_recent_activities():
    """Import from dashboard.py"""
    from components.dashboard import render_recent_activities as orig_func
    return orig_func()

def render_risk_distribution_chart():
    """Import from dashboard.py"""
    from components.dashboard import render_risk_distribution_chart as orig_func
    return orig_func()

def render_checklist_trends():
    """Import from dashboard.py"""
    from components.dashboard import render_checklist_trends as orig_func
    return orig_func()