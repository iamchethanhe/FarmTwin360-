import streamlit as st
from datetime import datetime
from database import get_db
from models import Visitor, Farm
from utils import generate_qr_code
from translations import get_text

def render_visitor_interface():
    """Render visitor check-in interface"""
    st.title(get_text("visitor_check_in"))
    
    tabs = st.tabs([
        get_text("check_in"),
        "My Visit Status",
        get_text("sop_guidelines"),
        get_text("visitor_log")
    ])
    
    with tabs[0]:
        render_check_in_form()
    
    with tabs[1]:
        render_visitor_checkout()
    
    with tabs[2]:
        render_sop_guidelines()
    
    with tabs[3]:
        render_visitor_log()

def render_check_in_form():
    """Render visitor check-in form"""
    st.subheader(get_text("visitor_registration"))
    
    db = get_db()
    try:
        farms = db.query(Farm).all()
        
        if not farms:
            st.warning(get_text("no_farms_available"))
            return
        
        farm_options = {f"{farm.name} - {farm.location}": farm.id for farm in farms}
        
        with st.form("visitor_checkin_form"):
            # Visitor details
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input(
                    get_text("full_name"),
                    placeholder="Enter your full name"
                )
                
                email = st.text_input(
                    get_text("email"),
                    placeholder="your.email@company.com"
                )
            
            with col2:
                company = st.text_input(
                    get_text("company_organization"),
                    placeholder="Company or Organization name"
                )
                
                phone = st.text_input(
                    get_text("phone_number"),
                    placeholder="+1-234-567-8900"
                )
            
            # Visit details
            selected_farm_name = st.selectbox(
                get_text("select_farm"),
                options=list(farm_options.keys())
            )
            selected_farm_id = farm_options[selected_farm_name]
            
            purpose = st.text_area(
                get_text("purpose_of_visit"),
                placeholder="Please describe the purpose of your visit..."
            )
            
            # Acknowledgments
            st.subheader(get_text("acknowledgments"))
            
            health_check = st.checkbox(
                get_text("health_declaration"),
                help="I confirm that I am not showing any symptoms of illness"
            )
            
            biosecurity_check = st.checkbox(
                get_text("biosecurity_agreement"),
                help="I agree to follow all biosecurity protocols"
            )
            
            sop_check = st.checkbox(
                get_text("sop_agreement"),
                help="I have read and understood the Standard Operating Procedures"
            )
            
            submitted = st.form_submit_button(
                get_text("register_visit"),
                type="primary"
            )
            
            if submitted:
                # Validation
                if not all([name, email, purpose]):
                    st.error(get_text("fill_required_fields"))
                elif not all([health_check, biosecurity_check, sop_check]):
                    st.error(get_text("accept_all_agreements"))
                else:
                    # Generate QR code
                    visitor_code = f"VISITOR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{name.replace(' ', '_').upper()}"
                    qr_code_data = f"FarmTwin Visitor: {name}\nCode: {visitor_code}\nFarm: {selected_farm_name}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    
                    # Create visitor record
                    visitor = Visitor(
                        name=name,
                        company=company,
                        email=email,
                        phone=phone,
                        purpose=purpose,
                        qr_code=visitor_code,
                        check_in_time=datetime.utcnow(),
                        farm_id=selected_farm_id
                    )
                    
                    db.add(visitor)
                    db.commit()
                    
                    # Display success and QR code
                    st.success(get_text("registration_successful"))
                    
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.write("**Visit Details:**")
                        st.write(f"**Name:** {name}")
                        st.write(f"**Company:** {company}")
                        st.write(f"**Farm:** {selected_farm_name}")
                        st.write(f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                        st.write(f"**Visitor Code:** {visitor_code}")
                    
                    with col2:
                        st.write("**Your QR Code:**")
                        qr_img = generate_qr_code(qr_code_data)
                        st.image(f"data:image/png;base64,{qr_img}", width=200)
                        st.write("Please show this QR code at security checkpoints")
    
    finally:
        db.close()

def render_sop_guidelines():
    """Render Standard Operating Procedures"""
    st.subheader(get_text("sop_guidelines"))
    
    st.markdown("""
    ## Standard Operating Procedures for Farm Visitors
    
    ### Biosecurity Requirements
    
    #### Before Entering the Farm:
    1. **Health Check**
       - Confirm you are not experiencing any flu-like symptoms
       - Have not been in contact with sick animals in the past 48 hours
       - Complete the health declaration form
    
    2. **Clothing and Equipment**
       - Remove all jewelry and unnecessary items
       - Wear provided protective clothing and footwear
       - Use hand sanitizer before entering each facility
    
    3. **Vehicle Requirements**
       - Park only in designated visitor parking areas
       - Clean and disinfect vehicle tires if requested
       - Do not bring unauthorized vehicles into production areas
    
    ### During Your Visit:
    
    #### General Guidelines:
    - Stay with your designated guide at all times
    - Follow all posted signs and barriers
    - Do not touch animals unless specifically permitted
    - No eating, drinking, or smoking in production areas
    - Keep mobile phones and cameras secured when requested
    
    #### Emergency Procedures:
    - Know the location of emergency exits
    - Report any incidents immediately to your guide
    - Follow evacuation procedures if announced
    - Contact emergency services if life-threatening situation occurs
    
    ### After Your Visit:
    
    #### Departure Protocol:
    - Return all borrowed protective equipment
    - Use provided disinfection facilities
    - Complete visitor feedback form if requested
    - Check out with security before leaving
    
    ### Compliance Requirements:
    
    #### Documentation:
    - Maintain visitor logs for regulatory compliance
    - Provide identification when requested
    - Sign acknowledgment of biosecurity training
    
    #### Restrictions:
    - No unauthorized photography or recording
    - No removal of materials without permission
    - No sharing of proprietary information
    
    ---
    
    **Emergency Contact:** Farm Security: (555) 123-4567  
    **Medical Emergency:** Call 911 immediately
    
    *By proceeding with your visit, you acknowledge that you have read, understood, and agree to comply with all Standard Operating Procedures.*
    """)

def render_visitor_log():
    """Render visitor log (accessible to visitors and authorized personnel)"""
    if st.session_state.role not in ["admin", "manager", "vet", "visitor"]:
        st.warning(get_text("access_restricted"))
        return
    
    st.subheader(get_text("visitor_log"))
    
    db = get_db()
    try:
        visitors = db.query(Visitor).order_by(Visitor.check_in_time.desc()).limit(50).all()
        
        if visitors:
            visitor_data = []
            for visitor in visitors:
                visitor_data.append({
                    "Check-in Time": visitor.check_in_time.strftime("%Y-%m-%d %H:%M") if visitor.check_in_time else "N/A",
                    "Name": visitor.name,
                    "Company": visitor.company or "N/A",
                    "Email": visitor.email or "N/A",
                    "Phone": visitor.phone or "N/A",
                    "Purpose": visitor.purpose[:50] + "..." if visitor.purpose and len(visitor.purpose) > 50 else visitor.purpose,
                    "Farm": visitor.farm.name if visitor.farm else "N/A",
                    "QR Code": visitor.qr_code,
                    "Status": "Checked Out" if visitor.check_out_time else "On Site"
                })
            
            import pandas as pd
            df = pd.DataFrame(visitor_data)
            st.dataframe(df, use_container_width=True)
            
            # Export functionality
            csv = df.to_csv(index=False)
            st.download_button(
                label=get_text("download_csv"),
                data=csv,
                file_name=f"visitor_log_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info(get_text("no_visitors_logged"))
    
    finally:
        db.close()

def render_visitor_checkout():
    """Render visitor checkout interface"""
    st.subheader("My Visit Status & Checkout")
    
    # Search for visitor
    st.write("**Find Your Visit:**")
    search_method = st.radio(
        "Search by:",
        ["Email", "Name", "Visitor Code"],
        horizontal=True
    )
    
    db = get_db()
    try:
        search_value = None
        visitors = []
        
        if search_method == "Email":
            search_value = st.text_input("Enter your email", placeholder="your.email@company.com")
            if search_value:
                visitors = db.query(Visitor).filter(Visitor.email == search_value).order_by(Visitor.check_in_time.desc()).all()
        elif search_method == "Name":
            search_value = st.text_input("Enter your full name", placeholder="John Doe")
            if search_value:
                visitors = db.query(Visitor).filter(Visitor.name.ilike(f"%{search_value}%")).order_by(Visitor.check_in_time.desc()).all()
        else:  # Visitor Code
            search_value = st.text_input("Enter your visitor code", placeholder="VISITOR_20231027_123456_JOHN_DOE")
            if search_value:
                visitors = db.query(Visitor).filter(Visitor.qr_code == search_value).order_by(Visitor.check_in_time.desc()).all()
        
        if search_value and visitors:
            # Display current/active visit
            active_visits = [v for v in visitors if not v.check_out_time]
            if active_visits:
                st.success(f"Found {len(active_visits)} active visit(s)")
                
                for visitor in active_visits:
                    with st.container():
                        st.markdown("---")
                        st.write("### Current Visit")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Name:** {visitor.name}")
                            st.write(f"**Company:** {visitor.company or 'N/A'}")
                            st.write(f"**Email:** {visitor.email}")
                            st.write(f"**Phone:** {visitor.phone or 'N/A'}")
                        
                        with col2:
                            st.write(f"**Farm:** {visitor.farm.name if visitor.farm else 'N/A'}")
                            st.write(f"**Purpose:** {visitor.purpose}")
                            st.write(f"**Check-in:** {visitor.check_in_time.strftime('%Y-%m-%d %H:%M') if visitor.check_in_time else 'N/A'}")
                            st.write(f"**Visitor Code:** {visitor.qr_code}")
                        
                        # Checkout button
                        if st.button(f"Check Out", key=f"checkout_{visitor.id}", type="primary"):
                            if check_out_visitor(visitor.id):
                                st.success("✅ Checked out successfully!")
                                st.write(f"**Check-out Time:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("Failed to check out. Please contact support.")
            else:
                st.info("No active visits found. You may have already checked out.")
            
            # Display visit history
            st.markdown("---")
            st.write("### Visit History")
            
            if visitors:
                import pandas as pd
                history_data = []
                for v in visitors:
                    duration = "In Progress"
                    if v.check_out_time and v.check_in_time:
                        delta = v.check_out_time - v.check_in_time
                        hours = delta.total_seconds() / 3600
                        duration = f"{hours:.1f} hours"
                    
                    history_data.append({
                        "Check-in": v.check_in_time.strftime('%Y-%m-%d %H:%M') if v.check_in_time else 'N/A',
                        "Check-out": v.check_out_time.strftime('%Y-%m-%d %H:%M') if v.check_out_time else 'In Progress',
                        "Duration": duration,
                        "Farm": v.farm.name if v.farm else 'N/A',
                        "Purpose": v.purpose[:40] + "..." if v.purpose and len(v.purpose) > 40 else v.purpose,
                        "Status": "Completed" if v.check_out_time else "Active"
                    })
                
                df = pd.DataFrame(history_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No visit history found.")
        elif search_value and not visitors:
            st.warning("No visits found with the provided information. Please check and try again.")
    
    finally:
        db.close()

def check_out_visitor(visitor_id):
    """Check out a visitor"""
    db = get_db()
    try:
        visitor = db.query(Visitor).filter(Visitor.id == visitor_id).first()
        if visitor and not visitor.check_out_time:
            visitor.check_out_time = datetime.utcnow()
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        return False
    finally:
        db.close()
