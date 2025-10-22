import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from database import get_db, get_accessible_farm_ids
from models import Barn, Checklist, Incident, Alert, Farm
from utils import get_dashboard_metrics, display_alerts_sidebar, get_risk_color
from components.visualization import render_3d_farm
from translations import get_text
from ai_engine import risk_predictor

def render_dashboard():
    """Render main dashboard"""
    st.title(get_text("dashboard"))
    
    # Display alerts in sidebar
    display_alerts_sidebar()
    
    # Get metrics
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
    
    # Main content area
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
    
    # Update risks button (for admins/managers)
    if st.session_state.role in ["admin", "manager"]:
        if st.button(get_text("update_ai_predictions")):
            with st.spinner(get_text("updating_predictions")):
                success = risk_predictor.update_barn_risks()
                if success:
                    st.success(get_text("predictions_updated"))
                    st.rerun()
                else:
                    st.error(get_text("predictions_error"))

def render_recent_activities():
    """Render recent activities panel filtered by assigned farms"""
    db = get_db()
    try:
        # Get user's accessible farms
        user_id = st.session_state.get('user').id
        user_role = st.session_state.get('role')
        accessible_farm_ids = get_accessible_farm_ids(user_id, user_role, db)
        
        if not accessible_farm_ids:
            st.info("No farms assigned. Please contact admin.")
            return
        
        # Get barn IDs from accessible farms
        barns_in_farms = db.query(Barn).filter(Barn.farm_id.in_(accessible_farm_ids)).all()
        barn_ids = [b.id for b in barns_in_farms]
        
        if not barn_ids:
            st.info("No barns available in assigned farms.")
            return
        
        # Get recent checklists filtered by accessible barns
        recent_checklists = db.query(Checklist).filter(
            Checklist.barn_id.in_(barn_ids)
        ).order_by(
            Checklist.submitted_at.desc()
        ).limit(5).all()
        
        # Get recent incidents filtered by accessible barns
        recent_incidents = db.query(Incident).filter(
            Incident.barn_id.in_(barn_ids)
        ).order_by(
            Incident.reported_at.desc()
        ).limit(3).all()
        
        st.write("**Recent Checklists:**")
        for checklist in recent_checklists:
            barn_name = checklist.barn.name if checklist.barn else "Unknown"
            user_name = checklist.user.name if checklist.user else "Unknown"
            
            st.write(f"• {barn_name} - {user_name}")
            st.write(f"  *{checklist.submitted_at.strftime('%Y-%m-%d %H:%M')}*")
        
        st.write("**Recent Incidents:**")
        for incident in recent_incidents:
            barn_name = incident.barn.name if incident.barn else "Unknown"
            severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(incident.severity, "⚪")
            
            st.write(f"• {severity_icon} {barn_name}")
            st.write(f"  {incident.incident_type.replace('_', ' ').title()}")
            st.write(f"  *{incident.reported_at.strftime('%Y-%m-%d %H:%M')}*")
    
    finally:
        db.close()

def render_risk_distribution_chart():
    """Render risk distribution pie chart filtered by assigned farms"""
    db = get_db()
    try:
        # Get user's accessible farms
        user_id = st.session_state.get('user').id
        user_role = st.session_state.get('role')
        accessible_farm_ids = get_accessible_farm_ids(user_id, user_role, db)
        
        if not accessible_farm_ids:
            st.info("No farms assigned.")
            return
        
        barns = db.query(Barn).filter(Barn.farm_id.in_(accessible_farm_ids)).all()
        
        risk_counts = {"High": 0, "Medium": 0, "Low": 0}
        for barn in barns:
            risk_level = barn.risk_level.title() if barn.risk_level else "Low"
            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
        
        fig = px.pie(
            values=list(risk_counts.values()),
            names=list(risk_counts.keys()),
            color_discrete_map={
                "High": "#ff4444",
                "Medium": "#ffaa00",
                "Low": "#44ff44"
            }
        )
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    finally:
        db.close()

def render_checklist_trends():
    """Render checklist submission trends filtered by assigned farms"""
    db = get_db()
    try:
        # Get user's accessible farms
        user_id = st.session_state.get('user').id
        user_role = st.session_state.get('role')
        accessible_farm_ids = get_accessible_farm_ids(user_id, user_role, db)
        
        if not accessible_farm_ids:
            st.info("No farms assigned.")
            return
        
        # Get barn IDs from accessible farms
        barns_in_farms = db.query(Barn).filter(Barn.farm_id.in_(accessible_farm_ids)).all()
        barn_ids = [b.id for b in barns_in_farms]
        
        if not barn_ids:
            st.info("No barns available.")
            return
        
        # Get checklists from last 30 days filtered by accessible barns
        start_date = datetime.utcnow() - timedelta(days=30)
        checklists = db.query(Checklist).filter(
            Checklist.submitted_at >= start_date,
            Checklist.barn_id.in_(barn_ids)
        ).all()
        
        # Group by date
        daily_counts = {}
        for checklist in checklists:
            date = checklist.submitted_at.date()
            daily_counts[date] = daily_counts.get(date, 0) + 1
        
        if daily_counts:
            dates = list(daily_counts.keys())
            counts = list(daily_counts.values())
            
            fig = px.line(x=dates, y=counts, title="Daily Checklist Submissions")
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No checklist data available for the last 30 days")
    
    finally:
        db.close()
