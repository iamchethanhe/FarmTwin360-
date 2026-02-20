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
from components.approvals import render_manager_approvals
from components.notifications import render_notifications
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
    
    # Enhanced Custom CSS for Beautiful Green Theme
    st.markdown("""
    <style>
    /* Main container styling with animated gradient */
    .stApp {
        background: linear-gradient(135deg, #F1F8E9 0%, #E8F5E9 50%, #DCEDC8 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Header styling with enhanced effects */
    h1 {
        color: #1B5E20 !important;
        font-weight: 800 !important;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.15);
        letter-spacing: -0.5px;
    }
    
    h2, h3 {
        color: #2E7D32 !important;
        font-weight: 700 !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Enhanced Card styling with glassmorphism */
    .stMetric {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #4CAF50;
        box-shadow: 0 8px 16px rgba(76, 175, 80, 0.2), 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(76, 175, 80, 0.3), 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Enhanced Button styling with modern effects */
    .stButton>button {
        background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
        color: white;
        font-weight: 700;
        border-radius: 12px;
        border: none;
        padding: 0.75rem 2.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 6px 12px rgba(76, 175, 80, 0.4), 0 2px 4px rgba(0,0,0,0.1);
        letter-spacing: 0.5px;
        text-transform: uppercase;
        font-size: 0.9rem;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #388E3C 0%, #4CAF50 100%);
        box-shadow: 0 8px 16px rgba(76, 175, 80, 0.5), 0 4px 8px rgba(0,0,0,0.15);
        transform: translateY(-3px) scale(1.02);
    }
    
    .stButton>button:active {
        transform: translateY(-1px) scale(0.98);
        box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
    }
    
    /* Enhanced Input fields with modern design */
    .stTextInput>div>div>input, .stSelectbox>div>div>select, 
    .stNumberInput>div>div>input, .stTextArea>div>div>textarea {
        border: 2px solid #A5D6A7;
        border-radius: 12px;
        background-color: rgba(255, 255, 255, 0.95);
        color: #1B5E20;
        font-weight: 500;
        padding: 0.75rem 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .stTextInput>div>div>input:focus, .stSelectbox>div>div>select:focus,
    .stNumberInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 0 0.3rem rgba(76, 175, 80, 0.2), 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-1px);
    }
    
    /* Enhanced Sidebar styling with gradient and icons */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1B5E20 0%, #2E7D32 50%, #388E3C 100%);
        box-shadow: 4px 0 12px rgba(0,0,0,0.1);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] label {
        color: #E8F5E9 !important;
        font-weight: 600;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
    [data-testid="stSidebar"] .stSelectbox>div>div>select {
        background-color: rgba(255, 255, 255, 0.95);
        border: 2px solid #66BB6A;
        color: #1B5E20;
    }
    
    [data-testid="stSidebar"] .stCheckbox label {
        color: #E8F5E9 !important;
    }
    
    /* Enhanced Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #C8E6C9 0%, #A5D6A7 100%);
        border-radius: 12px;
        color: #1B5E20;
        font-weight: 700;
        padding: 1rem;
        border: 2px solid #81C784;
        transition: all 0.3s ease;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #A5D6A7 0%, #81C784 100%);
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Enhanced Success/Error/Warning messages */
    .stSuccess {
        background: linear-gradient(135deg, #C8E6C9 0%, #A5D6A7 100%);
        color: #1B5E20;
        border-left: 5px solid #4CAF50;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 8px rgba(76, 175, 80, 0.2);
        font-weight: 600;
    }
    
    .stError {
        background: linear-gradient(135deg, #FFCDD2 0%, #EF9A9A 100%);
        color: #C62828;
        border-left: 5px solid #F44336;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 8px rgba(244, 67, 54, 0.2);
        font-weight: 600;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #FFF9C4 0%, #FFF59D 100%);
        color: #F57F17;
        border-left: 5px solid #FFEB3B;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 8px rgba(255, 235, 59, 0.2);
        font-weight: 600;
    }
    
    /* Enhanced Data tables */
    .stDataFrame {
        border: 3px solid #81C784;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 6px 16px rgba(76, 175, 80, 0.2);
    }
    
    /* Enhanced Info boxes */
    .stInfo {
        background: linear-gradient(135deg, #E1F5FE 0%, #B3E5FC 100%);
        color: #01579B;
        border-left: 5px solid #2196F3;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 8px rgba(33, 150, 243, 0.2);
        font-weight: 600;
    }
    
    /* Enhanced Farm header with animation */
    .farm-header {
        background: linear-gradient(135deg, #388E3C 0%, #4CAF50 50%, #66BB6A 100%);
        background-size: 200% 200%;
        animation: headerGlow 3s ease-in-out infinite;
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 12px 24px rgba(76, 175, 80, 0.4), 0 4px 8px rgba(0,0,0,0.1);
        border: 3px solid rgba(255, 255, 255, 0.3);
    }
    
    @keyframes headerGlow {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* Enhanced Risk indicators with modern badges */
    .risk-high {
        background: linear-gradient(135deg, #EF5350 0%, #F44336 100%);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        font-weight: 800;
        display: inline-block;
        box-shadow: 0 4px 8px rgba(244, 67, 54, 0.3);
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
    }
    
    .risk-medium {
        background: linear-gradient(135deg, #FFEB3B 0%, #FFC107 100%);
        color: #F57F17;
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        font-weight: 800;
        display: inline-block;
        box-shadow: 0 4px 8px rgba(255, 193, 7, 0.3);
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
    }
    
    .risk-low {
        background: linear-gradient(135deg, #66BB6A 0%, #4CAF50 100%);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        font-weight: 800;
        display: inline-block;
        box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
    }
    
    /* Form styling */
    .stForm {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        border: 2px solid #A5D6A7;
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #C8E6C9 0%, #A5D6A7 100%);
        border-radius: 10px;
        color: #1B5E20;
        font-weight: 700;
        padding: 10px 20px;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, #A5D6A7 0%, #81C784 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%) !important;
        color: white !important;
        border: 2px solid #2E7D32 !important;
    }
    
    /* Checkbox and Radio styling */
    .stCheckbox, .stRadio {
        color: #1B5E20;
        font-weight: 600;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: #E8F5E9;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
        border-radius: 10px;
        border: 2px solid #E8F5E9;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #388E3C 0%, #4CAF50 100%);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Language selector and voice toggle in sidebar
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
            "ਪੰਜಾਬੀ": "pa",
            "ଓଡ଼ିଆ": "or"
        }
        selected_lang = st.selectbox("🌍 Language", list(languages.keys()))
        set_language(languages[selected_lang])
        
        # Voice assistance toggle
        if 'voice_enabled' not in st.session_state:
            st.session_state.voice_enabled = False
        
        voice_enabled = st.checkbox("🔊 Enable Voice Assistant", value=st.session_state.voice_enabled)
        st.session_state.voice_enabled = voice_enabled
        
        if voice_enabled:
            st.info("Voice assistant is active. Important messages will be spoken.")
    
    # Add Web Speech API integration
    if st.session_state.get('voice_enabled', False):
        lang_code = languages[selected_lang]
        voice_lang_map = {
            "en": "en-US",
            "es": "es-ES",
            "hi": "hi-IN",
            "ta": "ta-IN",
            "te": "te-IN",
            "bn": "bn-IN",
            "mr": "mr-IN",
            "gu": "gu-IN",
            "kn": "kn-IN",
            "ml": "ml-IN",
            "pa": "pa-IN",
            "or": "or-IN"
        }
        speech_lang = voice_lang_map.get(lang_code, "en-US")
        
        st.markdown(f"""
        <script>
        // Web Speech API Text-to-Speech functionality
        let speechEnabled = true;
        let currentLang = '{speech_lang}';
        
        // Initialize speech synthesis
        function speak(text) {{
            if (!speechEnabled || !window.speechSynthesis) return;
            
            // Cancel any ongoing speech
            window.speechSynthesis.cancel();
            
            // Create utterance
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = currentLang;
            utterance.rate = 0.9;
            utterance.pitch = 1.0;
            utterance.volume = 1.0;
            
            // Speak
            window.speechSynthesis.speak(utterance);
        }}
        
        // Auto-speak success and error messages
        const observer = new MutationObserver(function(mutations) {{
            mutations.forEach(function(mutation) {{
                mutation.addedNodes.forEach(function(node) {{
                    if (node.className && typeof node.className === 'string') {{
                        if (node.className.includes('stSuccess')) {{
                            const text = node.textContent || node.innerText;
                            if (text) speak(text);
                        }} else if (node.className.includes('stError')) {{
                            const text = node.textContent || node.innerText;
                            if (text) speak("Error: " + text);
                        }} else if (node.className.includes('stWarning')) {{
                            const text = node.textContent || node.innerText;
                            if (text) speak("Warning: " + text);
                        }} else if (node.className.includes('stInfo')) {{
                            const text = node.textContent || node.innerText;
                            if (text) speak(text);
                        }}
                    }}
                }});
            }});
        }});
        
        // Start observing
        if (document.body) {{
            observer.observe(document.body, {{
                childList: true,
                subtree: true
            }});
        }}
        
        // Add click event to speak button text
        document.addEventListener('DOMContentLoaded', function() {{
            // Speak welcome message on load
            setTimeout(() => {{
                speak("Welcome to Farm Twin 360");
            }}, 1000);
        }});
        </script>
        """, unsafe_allow_html=True)
    
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
        
        # Render notifications in sidebar
        render_notifications()
    
    # Check for quick action navigation
    if st.session_state.get('show_admin_section'):
        render_admin_panel()
        return
    
    if st.session_state.get('show_manager_approvals'):
        render_manager_approvals()
        return
    
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
    elif selected == "Approvals":
        render_manager_approvals()

def get_menu_options(role):
    base_options = [get_text("dashboard")]
    
    if role == "admin":
        return base_options + [get_text("admin_panel"), get_text("analytics")]
    elif role == "manager":
        return base_options + ["Approvals", get_text("analytics")]
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
        return base_icons + ["check2-circle", "graph-up"]
    elif role == "worker":
        return base_icons + ["clipboard"]
    elif role == "visitor":
        return ["door-open"]
    elif role in ["vet", "auditor"]:
        return base_icons + ["graph-up"]
    
    return base_icons

if __name__ == "__main__":
    main()
