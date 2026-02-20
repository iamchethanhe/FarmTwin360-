import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from database import get_db
from models import Barn, Checklist, Incident, Alert
from utils import check_permissions, export_data_to_csv
from translations import get_text

def render_analytics():
    """Render analytics dashboard"""
    if not check_permissions(["admin", "manager", "vet", "auditor"]):
        st.error(get_text("access_denied"))
        return
    
    st.title(get_text("analytics_dashboard"))
    
    # Date range selector
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            get_text("start_date"),
            value=datetime.now().date() - timedelta(days=30)
        )
    
    with col2:
        end_date = st.date_input(
            get_text("end_date"),
            value=datetime.now().date()
        )
    
    # Analytics tabs
    tabs = st.tabs([
        get_text("risk_analysis"),
        get_text("mortality_trends"),
        get_text("hygiene_scores"),
        get_text("incident_reports"),
        get_text("compliance_report")
    ])
    
    with tabs[0]:
        render_risk_analysis(start_date, end_date)
    
    with tabs[1]:
        render_mortality_trends(start_date, end_date)
    
    with tabs[2]:
        render_hygiene_analysis(start_date, end_date)
    
    with tabs[3]:
        render_incident_analysis(start_date, end_date)
    
    with tabs[4]:
        render_compliance_report(start_date, end_date)

def render_risk_analysis(start_date, end_date):
    """Render risk analysis charts"""
    st.subheader(get_text("risk_analysis"))
    
    db = get_db()
    try:
        # Current risk distribution
        barns = db.query(Barn).all()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Current Risk Distribution**")
            
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
                },
                title="Risk Level Distribution"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.write("**Barn Risk Heatmap**")
            
            if barns:
                barn_data = []
                for barn in barns:
                    risk_numeric = {"high": 3, "medium": 2, "low": 1}.get(barn.risk_level, 1)
                    barn_data.append({
                        "Barn": barn.name,
                        "X": barn.position_x,
                        "Y": barn.position_y,
                        "Risk": risk_numeric,
                        "Risk_Label": barn.risk_level.title() if barn.risk_level else "Low"
                    })
                
                df = pd.DataFrame(barn_data)
                
                fig = px.scatter(
                    df, x="X", y="Y", 
                    color="Risk",
                    size="Risk",
                    hover_name="Barn",
                    hover_data=["Risk_Label"],
                    color_continuous_scale=["green", "yellow", "red"],
                    title="Farm Risk Heatmap"
                )
                
                fig.update_layout(
                    xaxis_title="Position X",
                    yaxis_title="Position Y"
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Risk trends over time
        st.write("**Risk Trends Over Time**")
        
        checklists = db.query(Checklist).filter(
            Checklist.submitted_at >= start_date,
            Checklist.submitted_at <= end_date,
            Checklist.approved == True
        ).all()
        
        if checklists:
            from ai_engine import risk_predictor
            
            trend_data = []
            for checklist in checklists:
                features = [
                    checklist.hygiene_score or 7,
                    checklist.mortality_count or 0,
                    checklist.feed_quality or 8,
                    checklist.water_quality or 8,
                    checklist.ventilation_score or 7,
                    checklist.temperature or 22,
                    checklist.humidity or 55
                ]
                
                risk_level, _ = risk_predictor.predict_risk(features)
                risk_label = risk_predictor.get_risk_label(risk_level)
                
                trend_data.append({
                    "Date": checklist.submitted_at.date(),
                    "Barn": checklist.barn.name if checklist.barn else "Unknown",
                    "Risk_Level": risk_label,
                    "Risk_Numeric": {"High": 3, "Medium": 2, "Low": 1}[risk_label]
                })
            
            if trend_data:
                df = pd.DataFrame(trend_data)
                
                # Group by date and calculate average risk
                daily_risk = df.groupby("Date")["Risk_Numeric"].mean().reset_index()
                
                fig = px.line(
                    daily_risk, x="Date", y="Risk_Numeric",
                    title="Average Risk Level Trend",
                    labels={"Risk_Numeric": "Average Risk Level"}
                )
                
                fig.update_layout(
                    yaxis=dict(
                        tickmode="array",
                        tickvals=[1, 2, 3],
                        ticktext=["Low", "Medium", "High"]
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    finally:
        db.close()

def render_mortality_trends(start_date, end_date):
    """Render mortality trend analysis"""
    st.subheader(get_text("mortality_trends"))
    
    db = get_db()
    try:
        checklists = db.query(Checklist).filter(
            Checklist.submitted_at >= start_date,
            Checklist.submitted_at <= end_date,
            Checklist.approved == True
        ).all()
        
        if checklists:
            mortality_data = []
            for checklist in checklists:
                mortality_data.append({
                    "Date": checklist.submitted_at.date(),
                    "Barn": checklist.barn.name if checklist.barn else "Unknown",
                    "Mortality_Count": checklist.mortality_count or 0
                })
            
            df = pd.DataFrame(mortality_data)
            
            # Daily totals
            daily_mortality = df.groupby("Date")["Mortality_Count"].sum().reset_index()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Daily Mortality Trend**")
                
                fig = px.line(
                    daily_mortality, x="Date", y="Mortality_Count",
                    title="Daily Mortality Count"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.write("**Mortality by Barn**")
                
                barn_mortality = df.groupby("Barn")["Mortality_Count"].sum().reset_index()
                
                fig = px.bar(
                    barn_mortality, x="Barn", y="Mortality_Count",
                    title="Total Mortality by Barn"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Statistics
            total_mortality = df["Mortality_Count"].sum()
            avg_daily = daily_mortality["Mortality_Count"].mean()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Mortality", total_mortality)
            with col2:
                st.metric("Average Daily", f"{avg_daily:.1f}")
            with col3:
                highest_day = daily_mortality.loc[daily_mortality["Mortality_Count"].idxmax()]
                st.metric("Highest Single Day", f"{highest_day['Mortality_Count']} ({highest_day['Date']})")
        
        else:
            st.info("No mortality data available for the selected period")
    
    finally:
        db.close()

def render_hygiene_analysis(start_date, end_date):
    """Render hygiene score analysis"""
    st.subheader(get_text("hygiene_analysis"))
    
    db = get_db()
    try:
        checklists = db.query(Checklist).filter(
            Checklist.submitted_at >= start_date,
            Checklist.submitted_at <= end_date,
            Checklist.approved == True
        ).all()
        
        if checklists:
            hygiene_data = []
            for checklist in checklists:
                hygiene_data.append({
                    "Date": checklist.submitted_at.date(),
                    "Barn": checklist.barn.name if checklist.barn else "Unknown",
                    "Hygiene_Score": checklist.hygiene_score or 0,
                    "Feed_Quality": checklist.feed_quality or 0,
                    "Water_Quality": checklist.water_quality or 0,
                    "Ventilation_Score": checklist.ventilation_score or 0
                })
            
            df = pd.DataFrame(hygiene_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Average Hygiene Scores by Barn**")
                
                barn_hygiene = df.groupby("Barn").agg({
                    "Hygiene_Score": "mean",
                    "Feed_Quality": "mean",
                    "Water_Quality": "mean",
                    "Ventilation_Score": "mean"
                }).round(1)
                
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    name="Hygiene",
                    x=barn_hygiene.index,
                    y=barn_hygiene["Hygiene_Score"]
                ))
                
                fig.add_trace(go.Bar(
                    name="Feed Quality",
                    x=barn_hygiene.index,
                    y=barn_hygiene["Feed_Quality"]
                ))
                
                fig.add_trace(go.Bar(
                    name="Water Quality",
                    x=barn_hygiene.index,
                    y=barn_hygiene["Water_Quality"]
                ))
                
                fig.add_trace(go.Bar(
                    name="Ventilation",
                    x=barn_hygiene.index,
                    y=barn_hygiene["Ventilation_Score"]
                ))
                
                fig.update_layout(
                    title="Quality Scores by Barn",
                    barmode="group",
                    yaxis_title="Score (1-10)"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.write("**Hygiene Trends Over Time**")
                
                daily_hygiene = df.groupby("Date")["Hygiene_Score"].mean().reset_index()
                
                fig = px.line(
                    daily_hygiene, x="Date", y="Hygiene_Score",
                    title="Average Daily Hygiene Score"
                )
                
                fig.update_layout(yaxis_range=[0, 10])
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Score distribution
            st.write("**Score Distribution**")
            
            fig = go.Figure()
            
            fig.add_trace(go.Histogram(
                x=df["Hygiene_Score"],
                name="Hygiene",
                opacity=0.7,
                nbinsx=10
            ))
            
            fig.update_layout(
                title="Hygiene Score Distribution",
                xaxis_title="Score",
                yaxis_title="Frequency"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Export data
            if st.button("Export Hygiene Data"):
                export_data_to_csv(hygiene_data, f"hygiene_analysis_{start_date}_{end_date}.csv")
        
        else:
            st.info("No hygiene data available for the selected period")
    
    finally:
        db.close()

def render_incident_analysis(start_date, end_date):
    """Render incident analysis"""
    st.subheader(get_text("incident_analysis"))
    
    db = get_db()
    try:
        incidents = db.query(Incident).filter(
            Incident.reported_at >= start_date,
            Incident.reported_at <= end_date,
            Incident.approved == True
        ).all()
        
        if incidents:
            incident_data = []
            for incident in incidents:
                incident_data.append({
                    "Date": incident.reported_at.date(),
                    "Barn": incident.barn.name if incident.barn else "Unknown",
                    "Type": incident.incident_type.replace("_", " ").title(),
                    "Severity": incident.severity.title(),
                    "Resolved": incident.resolved,
                    "Reporter": incident.user.name if incident.user else "Unknown"
                })
            
            df = pd.DataFrame(incident_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Incidents by Type**")
                
                type_counts = df["Type"].value_counts()
                
                fig = px.pie(
                    values=type_counts.values,
                    names=type_counts.index,
                    title="Incident Distribution by Type"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.write("**Incidents by Severity**")
                
                severity_counts = df["Severity"].value_counts()
                
                fig = px.bar(
                    x=severity_counts.index,
                    y=severity_counts.values,
                    title="Incident Count by Severity",
                    color=severity_counts.index,
                    color_discrete_map={
                        "High": "#ff4444",
                        "Medium": "#ffaa00",
                        "Low": "#44ff44"
                    }
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Resolution status
            col1, col2 = st.columns(2)
            
            with col1:
                resolved_count = df["Resolved"].sum()
                total_count = len(df)
                resolution_rate = (resolved_count / total_count * 100) if total_count > 0 else 0
                
                st.metric("Resolution Rate", f"{resolution_rate:.1f}%")
                st.metric("Resolved", resolved_count)
                st.metric("Unresolved", total_count - resolved_count)
            
            with col2:
                st.write("**Incidents Over Time**")
                
                daily_incidents = df.groupby("Date").size().reset_index(name="Count")
                
                fig = px.line(
                    daily_incidents, x="Date", y="Count",
                    title="Daily Incident Count"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Detailed incident table
            st.write("**Incident Details**")
            st.dataframe(df, use_container_width=True)
            
            # Export data
            if st.button("Export Incident Data"):
                export_data_to_csv(incident_data, f"incident_analysis_{start_date}_{end_date}.csv")
        
        else:
            st.info("No incidents reported during the selected period")
    
    finally:
        db.close()

def render_compliance_report(start_date, end_date):
    """Render compliance report"""
    st.subheader(get_text("compliance_report"))
    
    db = get_db()
    try:
        # Checklist compliance
        barns = db.query(Barn).all()
        
        compliance_data = []
        for barn in barns:
            checklists = db.query(Checklist).filter(
                Checklist.barn_id == barn.id,
                Checklist.submitted_at >= start_date,
                Checklist.submitted_at <= end_date,
                Checklist.approved == True
            ).count()
            
            # Expected checklists (1 per day)
            days = (datetime.now().date() - start_date).days + 1
            expected = min(days, (end_date - start_date).days + 1)
            
            compliance_rate = (checklists / expected * 100) if expected > 0 else 0
            
            compliance_data.append({
                "Barn": barn.name,
                "Expected_Checklists": expected,
                "Submitted_Checklists": checklists,
                "Compliance_Rate": compliance_rate,
                "Status": "Compliant" if compliance_rate >= 80 else "Non-Compliant"
            })
        
        df = pd.DataFrame(compliance_data)
        
        # Compliance metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_compliance = df["Compliance_Rate"].mean()
            st.metric("Average Compliance", f"{avg_compliance:.1f}%")
        
        with col2:
            compliant_barns = len(df[df["Status"] == "Compliant"])
            st.metric("Compliant Barns", f"{compliant_barns}/{len(df)}")
        
        with col3:
            total_expected = df["Expected_Checklists"].sum()
            total_submitted = df["Submitted_Checklists"].sum()
            overall_rate = (total_submitted / total_expected * 100) if total_expected > 0 else 0
            st.metric("Overall Rate", f"{overall_rate:.1f}%")
        
        # Compliance chart
        fig = px.bar(
            df, x="Barn", y="Compliance_Rate",
            title="Checklist Compliance by Barn",
            color="Status",
            color_discrete_map={
                "Compliant": "#44ff44",
                "Non-Compliant": "#ff4444"
            }
        )
        
        fig.add_hline(y=80, line_dash="dash", line_color="orange", 
                      annotation_text="80% Compliance Threshold")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed compliance table
        st.write("**Detailed Compliance Report**")
        st.dataframe(df, use_container_width=True)
        
        # Generate PDF report (placeholder)
        if st.button("Generate PDF Report"):
            st.info("PDF generation feature would be implemented with ReportLab")
        
        # Export data
        if st.button("Export Compliance Data"):
            export_data_to_csv(compliance_data, f"compliance_report_{start_date}_{end_date}.csv")
    
    finally:
        db.close()
