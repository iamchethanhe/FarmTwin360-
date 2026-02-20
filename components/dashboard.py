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
from components.role_dashboards import (
    render_admin_dashboard,
    render_manager_dashboard,
    render_worker_dashboard,
    render_vet_dashboard,
    render_auditor_dashboard,
    render_visitor_dashboard,
    render_default_dashboard
)

def render_dashboard():
    """Render main dashboard - routes to role-specific dashboards"""
    st.title(get_text("dashboard"))
    
    user_role = st.session_state.role
    
    # Route to role-specific dashboard
    if user_role == "admin":
        render_admin_dashboard()
    elif user_role == "manager":
        render_manager_dashboard()
    elif user_role == "worker":
        render_worker_dashboard()
    elif user_role == "vet":
        render_vet_dashboard()
    elif user_role == "auditor":
        render_auditor_dashboard()
    elif user_role == "visitor":
        render_visitor_dashboard()
    else:
        render_default_dashboard()

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
        
# Get recent checklists filtered by accessible barns (approved only)
        recent_checklists = db.query(Checklist).filter(
            Checklist.barn_id.in_(barn_ids),
            Checklist.approved == True
        ).order_by(
            Checklist.submitted_at.desc()
        ).limit(5).all()
        
        # Get recent incidents filtered by accessible barns (approved only)
        recent_incidents = db.query(Incident).filter(
            Incident.barn_id.in_(barn_ids),
            Incident.approved == True
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
        
# Get checklists from last 30 days filtered by accessible barns (approved only)
        start_date = datetime.utcnow() - timedelta(days=30)
        checklists = db.query(Checklist).filter(
            Checklist.submitted_at >= start_date,
            Checklist.barn_id.in_(barn_ids),
            Checklist.approved == True
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
