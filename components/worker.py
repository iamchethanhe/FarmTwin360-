import streamlit as st
import pandas as pd
from datetime import datetime
from database import get_db
from models import Barn, Checklist, Incident
from utils import save_uploaded_file, create_alert
from translations import get_text
from ai_engine import risk_predictor

def render_worker_interface():
    """Render worker interface for data input"""
    st.title(get_text("worker_interface"))
    
    tabs = st.tabs([
        get_text("submit_checklist"),
        get_text("report_incident"),
        get_text("my_submissions")
    ])
    
    with tabs[0]:
        render_checklist_form()
    
    with tabs[1]:
        render_incident_form()
    
    with tabs[2]:
        render_my_submissions()

def render_checklist_form():
    """Render checklist submission form"""
    st.subheader(get_text("daily_checklist"))
    
    db = get_db()
    try:
        barns = db.query(Barn).all()
        
        if not barns:
            st.warning(get_text("no_barns_available"))
            return
        
        barn_options = {f"{barn.name}": barn.id for barn in barns}
        
        with st.form("checklist_form"):
            # Barn selection
            selected_barn_name = st.selectbox(
                get_text("select_barn"),
                options=list(barn_options.keys())
            )
            selected_barn_id = barn_options[selected_barn_name]
            
            # Checklist fields
            col1, col2 = st.columns(2)
            
            with col1:
                hygiene_score = st.slider(
                    get_text("hygiene_score"),
                    min_value=1, max_value=10, value=8,
                    help="Rate the overall cleanliness and hygiene (1=Very Poor, 10=Excellent)"
                )
                
                mortality_count = st.number_input(
                    get_text("mortality_count"),
                    min_value=0, max_value=50, value=0,
                    help="Number of animals that died today"
                )
                
                feed_quality = st.slider(
                    get_text("feed_quality"),
                    min_value=1, max_value=10, value=8,
                    help="Rate the feed quality (1=Very Poor, 10=Excellent)"
                )
                
                water_quality = st.slider(
                    get_text("water_quality"),
                    min_value=1, max_value=10, value=8,
                    help="Rate the water quality (1=Very Poor, 10=Excellent)"
                )
            
            with col2:
                ventilation_score = st.slider(
                    get_text("ventilation_score"),
                    min_value=1, max_value=10, value=7,
                    help="Rate the ventilation system (1=Very Poor, 10=Excellent)"
                )
                
                temperature = st.number_input(
                    get_text("temperature_celsius"),
                    min_value=-10.0, max_value=50.0, value=22.0,
                    step=0.1,
                    help="Current temperature in Celsius"
                )
                
                humidity = st.number_input(
                    get_text("humidity_percentage"),
                    min_value=0.0, max_value=100.0, value=55.0,
                    step=0.1,
                    help="Current humidity percentage"
                )
            
            # GPS coordinates
            st.subheader(get_text("location_data"))
            col1, col2 = st.columns(2)
            
            with col1:
                gps_lat = st.number_input(
                    get_text("latitude"),
                    value=37.7749,
                    step=0.000001,
                    format="%.6f",
                    help="GPS Latitude coordinate"
                )
            
            with col2:
                gps_lng = st.number_input(
                    get_text("longitude"),
                    value=-122.4194,
                    step=0.000001,
                    format="%.6f",
                    help="GPS Longitude coordinate"
                )
            
            # Notes and photo
            notes = st.text_area(
                get_text("notes"),
                placeholder="Any additional observations or comments..."
            )
            
            uploaded_file = st.file_uploader(
                get_text("upload_photo"),
                type=['png', 'jpg', 'jpeg'],
                help="Optional: Upload a photo related to this checklist"
            )
            
            submitted = st.form_submit_button(
                get_text("submit_checklist"),
                type="primary"
            )
            
            if submitted:
                # Save uploaded file
                photo_path = None
                if uploaded_file:
                    photo_path = save_uploaded_file(uploaded_file)
                
                # Create checklist record
                checklist = Checklist(
                    barn_id=selected_barn_id,
                    user_id=st.session_state.user.id,
                    hygiene_score=hygiene_score,
                    mortality_count=mortality_count,
                    feed_quality=feed_quality,
                    water_quality=water_quality,
                    ventilation_score=ventilation_score,
                    temperature=temperature,
                    humidity=humidity,
                    notes=notes,
                    gps_lat=gps_lat,
                    gps_lng=gps_lng,
                    photo_path=photo_path
                )
                
                db.add(checklist)
                db.commit()
                
                # Predict risk for this barn
                features = [
                    hygiene_score, mortality_count, feed_quality,
                    water_quality, ventilation_score, temperature, humidity
                ]
                
                risk_level, probabilities = risk_predictor.predict_risk(features)
                risk_label = risk_predictor.get_risk_label(risk_level)
                
                # Update barn risk level
                barn = db.query(Barn).filter(Barn.id == selected_barn_id).first()
                if barn:
                    barn.risk_level = risk_label.lower()
                    barn.last_updated = datetime.utcnow()
                    db.commit()
                
                # Create alert if high risk
                if risk_label == "High":
                    create_alert(
                        "high_risk",
                        f"High risk detected in {selected_barn_name} after latest checklist submission",
                        "high",
                        barn_id=selected_barn_id,
                        user_id=st.session_state.user.id
                    )
                
                st.success(f"Checklist submitted successfully! Predicted risk level: **{risk_label}**")
                st.balloons()
    
    finally:
        db.close()

def render_incident_form():
    """Render incident reporting form"""
    st.subheader(get_text("incident_report"))
    
    db = get_db()
    try:
        barns = db.query(Barn).all()
        
        if not barns:
            st.warning(get_text("no_barns_available"))
            return
        
        barn_options = {f"{barn.name}": barn.id for barn in barns}
        
        with st.form("incident_form"):
            # Barn selection
            selected_barn_name = st.selectbox(
                get_text("select_barn"),
                options=list(barn_options.keys())
            )
            selected_barn_id = barn_options[selected_barn_name]
            
            # Incident details
            col1, col2 = st.columns(2)
            
            with col1:
                incident_type = st.selectbox(
                    get_text("incident_type"),
                    ["disease", "equipment_failure", "environmental", "injury", "other"]
                )
                
                severity = st.selectbox(
                    get_text("severity"),
                    ["low", "medium", "high"]
                )
            
            with col2:
                resolved = st.checkbox(get_text("incident_resolved"))
            
            description = st.text_area(
                get_text("incident_description"),
                placeholder="Describe the incident in detail..."
            )
            
            actions_taken = st.text_area(
                get_text("actions_taken"),
                placeholder="What actions were taken to address this incident?"
            )
            
            uploaded_file = st.file_uploader(
                get_text("upload_photo"),
                type=['png', 'jpg', 'jpeg'],
                help="Optional: Upload a photo of the incident"
            )
            
            submitted = st.form_submit_button(
                get_text("submit_incident"),
                type="primary"
            )
            
            if submitted:
                if not description:
                    st.error(get_text("description_required"))
                else:
                    # Save uploaded file
                    photo_path = None
                    if uploaded_file:
                        photo_path = save_uploaded_file(uploaded_file)
                    
                    # Create incident record
                    incident = Incident(
                        barn_id=selected_barn_id,
                        user_id=st.session_state.user.id,
                        incident_type=incident_type,
                        severity=severity,
                        description=description,
                        actions_taken=actions_taken,
                        photo_path=photo_path,
                        resolved=resolved
                    )
                    
                    db.add(incident)
                    db.commit()
                    
                    # Create alert for high severity incidents
                    if severity == "high":
                        create_alert(
                            "incident",
                            f"High severity {incident_type} incident reported in {selected_barn_name}",
                            "high",
                            barn_id=selected_barn_id,
                            user_id=st.session_state.user.id
                        )
                    
                    st.success(get_text("incident_submitted"))
    
    finally:
        db.close()

def render_my_submissions():
    """Render user's submission history"""
    st.subheader(get_text("my_submissions"))
    
    db = get_db()
    try:
        # Get user's checklists
        checklists = db.query(Checklist).filter(
            Checklist.user_id == st.session_state.user.id
        ).order_by(Checklist.submitted_at.desc()).limit(20).all()
        
        # Get user's incidents
        incidents = db.query(Incident).filter(
            Incident.user_id == st.session_state.user.id
        ).order_by(Incident.reported_at.desc()).limit(10).all()
        
        # Display checklists
        if checklists:
            st.write("**Recent Checklists:**")
            
            checklist_data = []
            for checklist in checklists:
                checklist_data.append({
                    "Date": checklist.submitted_at.strftime("%Y-%m-%d %H:%M"),
                    "Barn": checklist.barn.name if checklist.barn else "Unknown",
                    "Hygiene": checklist.hygiene_score,
                    "Mortality": checklist.mortality_count,
                    "Temperature": f"{checklist.temperature}°C",
                    "Notes": checklist.notes[:50] + "..." if checklist.notes and len(checklist.notes) > 50 else checklist.notes
                })
            
            df = pd.DataFrame(checklist_data)
            st.dataframe(df, use_container_width=True)
        
        # Display incidents
        if incidents:
            st.write("**Recent Incidents:**")
            
            incident_data = []
            for incident in incidents:
                incident_data.append({
                    "Date": incident.reported_at.strftime("%Y-%m-%d %H:%M"),
                    "Barn": incident.barn.name if incident.barn else "Unknown",
                    "Type": incident.incident_type.replace("_", " ").title(),
                    "Severity": incident.severity.title(),
                    "Resolved": "Yes" if incident.resolved else "No",
                    "Description": incident.description[:50] + "..." if len(incident.description) > 50 else incident.description
                })
            
            df = pd.DataFrame(incident_data)
            st.dataframe(df, use_container_width=True)
        
        if not checklists and not incidents:
            st.info(get_text("no_submissions_yet"))
    
    finally:
        db.close()
