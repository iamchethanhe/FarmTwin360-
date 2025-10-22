import streamlit as st
import pandas as pd
from database import get_db
from models import User, Farm, Barn
from auth import create_user
from utils import validate_email, validate_password, check_permissions
from translations import get_text

def render_admin_panel():
    """Render admin panel with user and farm management"""
    if not check_permissions(["admin"]):
        st.error(get_text("access_denied"))
        return
    
    st.title("👑 " + get_text("admin_panel"))
    
    tabs = st.tabs([
        "👥 " + get_text("user_management"),
        "🏠 " + get_text("farm_management"),
        "🏭 Barn Management",
        "⚙️ " + get_text("system_settings")
    ])
    
    with tabs[0]:
        render_user_management()
    
    with tabs[1]:
        render_farm_management()
    
    with tabs[2]:
        render_barn_management()
    
    with tabs[3]:
        render_system_settings()

def render_user_management():
    """Render user management interface"""
    st.subheader(get_text("user_management"))
    
    # Add new user form
    with st.expander("➕ " + get_text("add_new_user")):
        with st.form("add_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input(get_text("name"))
                email = st.text_input(get_text("email"))
            
            with col2:
                password = st.text_input(get_text("password"), type="password")
                role = st.selectbox(
                    get_text("role"),
                    ["admin", "manager", "worker", "visitor", "vet", "auditor"]
                )
            
            # Farm assignment for managers
            farm_id = None
            if role == "manager":
                db_temp = get_db()
                try:
                    farms = db_temp.query(Farm).all()
                    if farms:
                        farm_options = {f"{farm.name} ({farm.location})": farm.id for farm in farms}
                        farm_options = {"None (No Farm Assigned)": None, **farm_options}
                        selected_farm = st.selectbox(
                            "🏠 Assign Farm (Managers only)",
                            options=list(farm_options.keys())
                        )
                        farm_id = farm_options[selected_farm]
                finally:
                    db_temp.close()
            
            submit = st.form_submit_button(get_text("create_user"))
            
            if submit:
                if not name or not email or not password:
                    st.error(get_text("fill_all_fields"))
                elif not validate_email(email):
                    st.error(get_text("invalid_email"))
                else:
                    valid_password, password_message = validate_password(password)
                    if not valid_password:
                        st.error(password_message)
                    else:
                        success, message = create_user(name, email, password, role, farm_id)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
    
    # Display existing users
    st.subheader(get_text("existing_users"))
    
    db = get_db()
    try:
        users = db.query(User).all()
        
        if users:
            user_data = []
            for user in users:
                farm_name = "N/A"
                if user.farm_id:
                    farm = db.query(Farm).filter(Farm.id == user.farm_id).first()
                    if farm:
                        farm_name = farm.name
                
                user_data.append({
                    "ID": user.id,
                    "Name": user.name,
                    "Email": user.email,
                    "Role": user.role,
                    "Assigned Farm": farm_name,
                    "Created": user.created_at.strftime("%Y-%m-%d"),
                    "Active": "Yes" if user.is_active else "No"
                })
            
            df = pd.DataFrame(user_data)
            st.dataframe(df, use_container_width=True)
            
            # User actions
            st.subheader(get_text("user_actions"))
            
            col1, col2 = st.columns(2)
            
            with col1:
                user_to_deactivate = st.selectbox(
                    get_text("deactivate_user"),
                    options=[f"{user.id} - {user.name}" for user in users if user.is_active],
                    index=None
                )
                
                if st.button(get_text("deactivate")) and user_to_deactivate:
                    user_id = int(user_to_deactivate.split(" - ")[0])
                    deactivate_user(user_id)
                    st.success(get_text("user_deactivated"))
                    st.rerun()
            
            with col2:
                user_to_activate = st.selectbox(
                    get_text("activate_user"),
                    options=[f"{user.id} - {user.name}" for user in users if not user.is_active],
                    index=None
                )
                
                if st.button(get_text("activate")) and user_to_activate:
                    user_id = int(user_to_activate.split(" - ")[0])
                    activate_user(user_id)
                    st.success(get_text("user_activated"))
                    st.rerun()
        else:
            st.info(get_text("no_users_found"))
    
    finally:
        db.close()

def render_farm_management():
    """Render farm management interface"""
    st.subheader("🏠 " + get_text("farm_management"))
    
    # Add new farm
    with st.expander("➕ " + get_text("add_new_farm")):
        with st.form("add_farm_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                farm_name = st.text_input(get_text("farm_name"))
                location = st.text_input(get_text("location"))
            
            with col2:
                description = st.text_area(get_text("description"))
            
            submit = st.form_submit_button(get_text("create_farm"))
            
            if submit:
                if not farm_name:
                    st.error(get_text("farm_name_required"))
                else:
                    success = create_farm(farm_name, location, description)
                    if success:
                        st.success(get_text("farm_created"))
                        st.rerun()
                    else:
                        st.error(get_text("farm_creation_error"))
    
    # Display existing farms
    st.subheader(get_text("existing_farms"))
    
    db = get_db()
    try:
        farms = db.query(Farm).all()
        
        if farms:
            for farm in farms:
                with st.expander(f"🏠 {farm.name}"):
                    st.write(f"**Location:** {farm.location or 'Not specified'}")
                    st.write(f"**Description:** {farm.description or 'No description'}")
                    st.write(f"**Created:** {farm.created_at.strftime('%Y-%m-%d')}")
                    
                    # Show barns for this farm
                    barns = db.query(Barn).filter(Barn.farm_id == farm.id).all()
                    st.write(f"**Barns:** {len(barns)}")
                    
                    if barns:
                        barn_data = []
                        for barn in barns:
                            barn_data.append({
                                "Name": barn.name,
                                "Capacity": barn.capacity,
                                "Risk Level": barn.risk_level.title() if barn.risk_level else "Unknown"
                            })
                        
                        barn_df = pd.DataFrame(barn_data)
                        st.dataframe(barn_df, use_container_width=True)
        else:
            st.info(get_text("no_farms_found"))
    
    finally:
        db.close()

def render_system_settings():
    """Render system settings"""
    st.subheader(get_text("system_settings"))
    
    # Database statistics
    st.write("**Database Statistics:**")
    
    db = get_db()
    try:
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
        
        # System actions
        st.write("**System Actions:**")
        
        if st.button("Reset Demo Data", type="secondary"):
            if st.checkbox("I understand this will reset all demo data"):
                from database import create_demo_data
                create_demo_data()
                st.success("Demo data has been reset")
                st.rerun()
    
    finally:
        db.close()

def create_farm(name, location, description):
    """Create a new farm"""
    db = get_db()
    try:
        farm = Farm(
            name=name,
            location=location,
            description=description
        )
        db.add(farm)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error creating farm: {e}")
        return False
    finally:
        db.close()

def deactivate_user(user_id):
    """Deactivate a user"""
    db = get_db()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_active = False
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        return False
    finally:
        db.close()

def activate_user(user_id):
    """Activate a user"""
    db = get_db()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_active = True
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        return False
    finally:
        db.close()
