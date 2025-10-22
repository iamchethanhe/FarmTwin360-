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
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for green theme
    st.markdown("""
    <style>
    /* Main container styling */
    .stApp {
        background: linear-gradient(135deg, #F1F8E9 0%, #E8F5E9 100%);
    }
    
    /* Header styling */
    h1 {
        color: #1B5E20 !important;
        font-weight: 700 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    h2, h3 {
        color: #2E7D32 !important;
        font-weight: 600 !important;
    }
    
    /* Card styling */
    .stMetric {
        background: linear-gradient(135deg, #ffffff 0%, #C8E6C9 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #4CAF50;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
        color: white;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(76, 175, 80, 0.3);
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #388E3C 0%, #4CAF50 100%);
        box-shadow: 0 6px 12px rgba(76, 175, 80, 0.4);
        transform: translateY(-2px);
    }
    
    /* Input fields */
    .stTextInput>div>div>input, .stSelectbox>div>div>select {
        border: 2px solid #A5D6A7;
        border-radius: 8px;
        background-color: #ffffff;
        color: #1B5E20;
        font-weight: 500;
    }
    
    .stTextInput>div>div>input:focus, .stSelectbox>div>div>select:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 0 0.2rem rgba(76, 175, 80, 0.25);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2E7D32 0%, #388E3C 100%);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #ffffff;
        font-weight: 500;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #C8E6C9 0%, #A5D6A7 100%);
        border-radius: 8px;
        color: #1B5E20;
        font-weight: 600;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: #C8E6C9;
        color: #1B5E20;
        border-left: 4px solid #4CAF50;
        border-radius: 8px;
    }
    
    .stError {
        background-color: #FFCDD2;
        color: #C62828;
        border-left: 4px solid #F44336;
        border-radius: 8px;
    }
    
    /* Data tables */
    .stDataFrame {
        border: 2px solid #A5D6A7;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: #E1F5FE;
        color: #01579B;
        border-left: 4px solid #2196F3;
        border-radius: 8px;
    }
    
    /* Farm icon styling */
    .farm-header {
        background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 16px rgba(76, 175, 80, 0.3);
    }
    
    /* Risk indicators */
    .risk-high {
        background: #FFCDD2;
        color: #C62828;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
    }
    
    .risk-medium {
        background: #FFF9C4;
        color: #F57F17;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
    }
    
    .risk-low {
        background: #C8E6C9;
        color: #1B5E20;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Language selector in sidebar
    with st.sidebar:
        languages = {
            "English": "en", 
            "Español": "es",
            "हिन्दी": "hi",
            "தமிழ்": "ta",
            "తెలుగు": "te",
            "বাংলা": "bn",
            "मराठी": "mr",
            "ગુજરાતી": "gu",
            "ಕನ್ನಡ": "kn",
            "മലയാളം": "ml",
            "ਪੰਜਾਬੀ": "pa",
            "ଓଡ଼ିଆ": "or"
        }
        selected_lang = st.selectbox("🌍 Language", list(languages.keys()))
        set_language(languages[selected_lang])
    
    # Authentication
    if not st.session_state.get('authenticated', False):
        render_login()
    else:
        render_main_app()

def render_login():
    # Beautiful header
    st.markdown("""
    <div class="farm-header">
        <h1 style="color: white; margin: 0; font-size: 3rem;">🌾 FarmTwin 360</h1>
        <p style="color: #E8F5E9; font-size: 1.2rem; margin-top: 0.5rem;">Digital Farm Management System</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.title(get_text("login_title"))
    
    # Demo users info
    with st.expander("👥 " + get_text("demo_users")):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("🔑 **Admin:** admin@farmtwin.com / admin123")
            st.markdown("👔 **Manager:** manager@farmtwin.com / manager123")
            st.markdown("👷 **Worker:** worker@farmtwin.com / worker123")
        with col2:
            st.markdown("👤 **Visitor:** visitor@farmtwin.com / visitor123")
            st.markdown("🩺 **Vet:** vet@farmtwin.com / vet123")
            st.markdown("📊 **Auditor:** auditor@farmtwin.com / auditor123")
    
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
    
    # Beautiful header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%); 
                padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem; 
                box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);">
        <h1 style="color: white; margin: 0; text-align: center; font-size: 2.5rem;">
            🌾 FarmTwin 360 - Digital Farm Management
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # User info header
    col1, col2, col3 = st.columns([3, 4, 3])
    with col1:
        st.markdown(f"### 👤 {get_text('welcome')}, {st.session_state.user.name}")
    with col2:
        role_icons = {
            "admin": "👑",
            "manager": "👔", 
            "worker": "👷",
            "visitor": "👤",
            "vet": "🩺",
            "auditor": "📊"
        }
        icon = role_icons.get(user_role, "👤")
        st.markdown(f"### {icon} {get_text('role')}: {user_role.title()}")
    with col3:
        if st.button("🚪 " + get_text("logout"), use_container_width=True):
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
