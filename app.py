import streamlit as st
import os
from streamlit_option_menu import option_menu
from auth import authenticate_user, get_user_role, logout_user, init_session_state
from database import init_database, create_demo_data
from components.dashboard import render_dashboard
from components.admin import render_admin_panel
from components.worker import render_worker_interface
from components.visitor import render_visitor_interface
from components.analytics import render_analytics
from translations import get_text, set_language

# Initialize session state
init_session_state()

# Initialize database
init_database()

# Create demo data if needed
if not st.session_state.get('demo_data_created', False):
    create_demo_data()
    st.session_state.demo_data_created = True

def main():
    st.set_page_config(
        page_title="FarmTwin 360",
        page_icon="🚜",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Language selector in sidebar
    with st.sidebar:
        languages = {"English": "en", "Español": "es"}
        selected_lang = st.selectbox("Language / Idioma", list(languages.keys()))
        set_language(languages[selected_lang])
    
    # Authentication
    if not st.session_state.get('authenticated', False):
        render_login()
    else:
        render_main_app()

def render_login():
    st.title(get_text("login_title"))
    
    # Demo users info
    with st.expander(get_text("demo_users")):
        st.write("**Admin:** admin@farmtwin.com / admin123")
        st.write("**Manager:** manager@farmtwin.com / manager123")
        st.write("**Worker:** worker@farmtwin.com / worker123")
        st.write("**Visitor:** visitor@farmtwin.com / visitor123")
        st.write("**Vet:** vet@farmtwin.com / vet123")
        st.write("**Auditor:** auditor@farmtwin.com / auditor123")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            email = st.text_input(get_text("email"))
            password = st.text_input(get_text("password"), type="password")
            submit = st.form_submit_button(get_text("login"))
            
            if submit:
                user = authenticate_user(email, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.session_state.role = user.role
                    st.success(get_text("login_success"))
                    st.rerun()
                else:
                    st.error(get_text("login_error"))

def render_main_app():
    user_role = st.session_state.role
    
    # Header
    col1, col2, col3 = st.columns([2, 4, 2])
    with col1:
        st.write(f"**{get_text('welcome')}** {st.session_state.user.name}")
        st.write(f"**{get_text('role')}:** {user_role}")
    
    with col2:
        st.title("🚜 FarmTwin 360")
    
    with col3:
        if st.button(get_text("logout")):
            logout_user()
            st.rerun()
    
    # Navigation based on role
    menu_options = get_menu_options(user_role)
    
    with st.sidebar:
        selected = option_menu(
            get_text("navigation"),
            menu_options,
            icons=get_menu_icons(user_role),
            menu_icon="cast",
            default_index=0,
        )
    
    # Render selected page
    if selected == get_text("dashboard"):
        render_dashboard()
    elif selected == get_text("admin_panel"):
        render_admin_panel()
    elif selected == get_text("worker_interface"):
        render_worker_interface()
    elif selected == get_text("visitor_check_in"):
        render_visitor_interface()
    elif selected == get_text("analytics"):
        render_analytics()

def get_menu_options(role):
    base_options = [get_text("dashboard")]
    
    if role == "admin":
        return base_options + [get_text("admin_panel"), get_text("analytics")]
    elif role == "manager":
        return base_options + [get_text("analytics")]
    elif role == "worker":
        return base_options + [get_text("worker_interface")]
    elif role == "visitor":
        return [get_text("visitor_check_in")]
    elif role in ["vet", "auditor"]:
        return base_options + [get_text("analytics")]
    
    return base_options

def get_menu_icons(role):
    base_icons = ["house"]
    
    if role == "admin":
        return base_icons + ["gear", "graph-up"]
    elif role == "manager":
        return base_icons + ["graph-up"]
    elif role == "worker":
        return base_icons + ["clipboard"]
    elif role == "visitor":
        return ["door-open"]
    elif role in ["vet", "auditor"]:
        return base_icons + ["graph-up"]
    
    return base_icons

if __name__ == "__main__":
    main()
