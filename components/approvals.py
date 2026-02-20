import streamlit as st
from datetime import datetime
from database import get_db, get_accessible_farm_ids
from models import Checklist, Incident, Barn
from utils import check_permissions, create_alert
from ai_engine import risk_predictor
from components.notifications import notify_worker_on_checklist_approval, notify_worker_on_incident_approval


def render_manager_approvals():
    """Managers approve worker-submitted checklists and incidents before they appear in dashboards/analytics."""
    if not check_permissions(["manager", "admin"]):
        st.error("Access denied.")
        return

    st.title("✅ Approvals - Review & Approve")
    
    # Get the section to display from quick action
    show_section = st.session_state.get('show_manager_approvals', None)
    
    # Create tabs for better organization
    tab1, tab2 = st.tabs(["📋 Pending Checklists", "⚠️ Pending Incidents"])

    db = get_db()
    try:
        # Determine farms this manager can access
        user_id = st.session_state.get('user').id
        user_role = st.session_state.get('role')
        accessible_farm_ids = get_accessible_farm_ids(user_id, user_role, db)

        # Pending Checklists (in manager's farms)
        with tab1:
            st.subheader("📋 Pending Checklists")
        pending_checklists = []
        if accessible_farm_ids:
            pending_checklists = (
                db.query(Checklist)
                .join(Barn, Checklist.barn_id == Barn.id)
                .filter(Checklist.approved == False, Barn.farm_id.in_(accessible_farm_ids))
                .order_by(Checklist.submitted_at.desc())
                .all()
            )
        if pending_checklists:
            for cl in pending_checklists:
                with st.expander(f"Barn: {cl.barn.name if cl.barn else 'Unknown'} | By: {cl.user.name if cl.user else 'Unknown'} | At: {cl.submitted_at.strftime('%Y-%m-%d %H:%M')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"Hygiene: {cl.hygiene_score}")
                        st.write(f"Mortality: {cl.mortality_count}")
                        st.write(f"Feed: {cl.feed_quality}")
                        st.write(f"Water: {cl.water_quality}")
                    with col2:
                        st.write(f"Ventilation: {cl.ventilation_score}")
                        st.write(f"Temp: {cl.temperature} °C")
                        st.write(f"Humidity: {cl.humidity} %")
                        if cl.notes:
                            st.write(f"Notes: {cl.notes}")
                    if st.button("Approve Checklist", key=f"approve_cl_{cl.id}"):
                        # Approve
                        cl.approved = True
                        cl.approved_by = user_id
                        cl.approved_at = datetime.utcnow()
                        db.commit()
                        
                        # Notify the worker
                        try:
                            approver_name = st.session_state.user.name
                            notify_worker_on_checklist_approval(cl, approver_name)
                        except Exception as e:
                            print(f"Warning: Failed to send approval notification: {e}")
                        
                        # After approval, compute risk and update barn
                        features = [
                            cl.hygiene_score or 7,
                            cl.mortality_count or 0,
                            cl.feed_quality or 8,
                            cl.water_quality or 8,
                            cl.ventilation_score or 7,
                            cl.temperature or 22,
                            cl.humidity or 55,
                        ]
                        risk_level, _ = risk_predictor.predict_risk(features)
                        risk_label = risk_predictor.get_risk_label(risk_level)
                        barn = db.query(Barn).filter(Barn.id == cl.barn_id).first()
                        if barn:
                            barn.risk_level = risk_label.lower()
                            barn.last_updated = datetime.utcnow()
                            db.commit()
                        # High risk alert
                        if risk_label == "High":
                            create_alert(
                                "high_risk",
                                f"High risk detected in {cl.barn.name if cl.barn else 'Barn'} after approved checklist",
                                "high",
                                barn_id=cl.barn_id,
                                user_id=cl.user_id,
                            )
                        st.success("✅ Checklist approved! Worker has been notified.")
                        st.rerun()
            else:
                st.info("No pending checklists.")
        
        # Pending Incidents (in manager's farms)
        with tab2:
            st.subheader("⚠️ Pending Incidents")
        pending_incidents = []
        if accessible_farm_ids:
            pending_incidents = (
                db.query(Incident)
                .join(Barn, Incident.barn_id == Barn.id)
                .filter(Incident.approved == False, Barn.farm_id.in_(accessible_farm_ids))
                .order_by(Incident.reported_at.desc())
                .all()
            )
            if pending_incidents:
                for inc in pending_incidents:
                    with st.expander(f"Barn: {inc.barn.name if inc.barn else 'Unknown'} | Type: {inc.incident_type} | Severity: {inc.severity.title()} | At: {inc.reported_at.strftime('%Y-%m-%d %H:%M')}"):
                        st.write(inc.description)
                        if inc.actions_taken:
                            st.write(f"Actions Taken: {inc.actions_taken}")
                        if st.button("Approve Incident", key=f"approve_inc_{inc.id}"):
                            inc.approved = True
                            inc.approved_by = user_id
                            inc.approved_at = datetime.utcnow()
                            db.commit()
                            
                            # Notify the worker
                            try:
                                approver_name = st.session_state.user.name
                                notify_worker_on_incident_approval(inc, approver_name)
                            except Exception as e:
                                print(f"Warning: Failed to send approval notification: {e}")
                            
                            # Create alert for high severity incidents after approval
                            if inc.severity == "high":
                                create_alert(
                                    "incident",
                                    f"High severity {inc.incident_type} incident approved in {inc.barn.name if inc.barn else 'Barn'}",
                                    "high",
                                    barn_id=inc.barn_id,
                                    user_id=inc.user_id,
                                )
                            st.success("✅ Incident approved! Worker has been notified.")
                            st.rerun()
            else:
                st.info("No pending incidents.")
    finally:
        db.close()
