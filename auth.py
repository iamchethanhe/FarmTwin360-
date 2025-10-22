import streamlit as st
import bcrypt
import jwt
from datetime import datetime, timedelta
from database import get_db
from models import User
import os

SECRET_KEY = os.getenv("SESSION_SECRET", "farmtwin-secret-key-change-in-production")

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'role' not in st.session_state:
        st.session_state.role = None

def hash_password(password: str) -> str:
    """Hash a password"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def authenticate_user(email: str, password: str):
    """Authenticate user with email and password"""
    db = get_db()
    try:
        user = db.query(User).filter(User.email == email, User.is_active == True).first()
        if user and verify_password(password, user.password_hash):
            return user
        return None
    finally:
        db.close()

def get_user_role(user_id: int) -> str:
    """Get user role by ID"""
    db = get_db()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        return user.role if user else None
    finally:
        db.close()

def create_jwt_token(user_id: int, role: str) -> str:
    """Create JWT token"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_jwt_token(token: str) -> dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def logout_user():
    """Logout current user"""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.role = None

def require_role(allowed_roles):
    """Decorator to require specific roles"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not st.session_state.get('authenticated', False):
                st.error("Please login to access this page")
                return
            
            if st.session_state.role not in allowed_roles:
                st.error("You don't have permission to access this page")
                return
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def create_user(name: str, email: str, password: str, role: str):
    """Create a new user"""
    db = get_db()
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            return False, "User with this email already exists"
        
        password_hash = hash_password(password)
        user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            role=role
        )
        db.add(user)
        db.commit()
        return True, "User created successfully"
    except Exception as e:
        db.rollback()
        return False, f"Error creating user: {str(e)}"
    finally:
        db.close()
