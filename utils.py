import streamlit as st
import qrcode
import io
import base64
from PIL import Image
import pandas as pd
from datetime import datetime
import os
from database import get_db, get_accessible_farm_ids
from models import Alert, User, Barn, Farm

def generate_qr_code(data):
    """Generate QR code for given data"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for display
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return img_str

def save_uploaded_file(uploaded_file, directory="uploads"):
    """Save uploaded file and return path"""
    if uploaded_file is not None:
        # Create directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{uploaded_file.name}"
        filepath = os.path.join(directory, filename)
        
        # Save file
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return filepath
    return None

def create_alert(alert_type, message, severity="medium", barn_id=None, user_id=None):
    """Create a new alert"""
    db = get_db()
    try:
        alert = Alert(
            type=alert_type,
            message=message,
            severity=severity,
            barn_id=barn_id,
            user_id=user_id
        )
        db.add(alert)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error creating alert: {e}")
        return False
    finally:
        db.close()

def get_unread_alerts():
    """Get unread alerts for current user"""
    db = get_db()
    try:
        alerts = db.query(Alert).filter(Alert.read == False).order_by(Alert.created_at.desc()).all()
        return alerts
    finally:
        db.close()

def mark_alert_read(alert_id):
    """Mark alert as read"""
    db = get_db()
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if alert:
            alert.read = True
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        return False
    finally:
        db.close()

def format_datetime(dt):
    """Format datetime for display"""
    if dt:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return "N/A"

def get_risk_color(risk_level):
    """Get color for risk level"""
    colors = {
        "high": "#ff4444",
        "medium": "#ffaa00",
        "low": "#44ff44"
    }
    return colors.get(risk_level.lower(), "#cccccc")

def export_data_to_csv(data, filename):
    """Export data to CSV"""
    df = pd.DataFrame(data)
    csv = df.to_csv(index=False)
    
    # Create download button
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=filename,
        mime="text/csv"
    )

def validate_email(email):
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, "Password is valid"

def check_permissions(required_roles):
    """Check if current user has required permissions"""
    if not st.session_state.get('authenticated', False):
        return False
    
    user_role = st.session_state.get('role')
    return user_role in required_roles

def display_alerts_sidebar():
    """Display alerts in sidebar"""
    alerts = get_unread_alerts()
    
    if alerts:
        with st.sidebar:
            st.subheader(f"🚨 Alerts ({len(alerts)})")
            
            for alert in alerts[:5]:  # Show only first 5 alerts
                severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(alert.severity, "⚪")
                
                with st.expander(f"{severity_icon} {alert.type.replace('_', ' ').title()}"):
                    st.write(alert.message)
                    st.write(f"*{format_datetime(alert.created_at)}*")
                    
                    if st.button(f"Mark as Read", key=f"alert_{alert.id}"):
                        mark_alert_read(alert.id)
                        st.rerun()

def get_dashboard_metrics():
    """Get key metrics for dashboard filtered by user's assigned farms"""
    db = get_db()
    try:
        from models import Barn, Checklist, Incident
        
        # Get user's accessible farms
        user_id = st.session_state.get('user').id
        user_role = st.session_state.get('role')
        accessible_farm_ids = get_accessible_farm_ids(user_id, user_role, db)
        
        if not accessible_farm_ids:
            # User has no assigned farms
            return {
                "total_barns": 0,
                "high_risk_barns": 0,
                "total_checklists": 0,
                "unresolved_incidents": 0
            }
        
        # Filter barns by accessible farms
        total_barns = db.query(Barn).filter(Barn.farm_id.in_(accessible_farm_ids)).count()
        high_risk_barns = db.query(Barn).filter(
            Barn.farm_id.in_(accessible_farm_ids),
            Barn.risk_level == "high"
        ).count()
        
        # Filter checklists by barns in accessible farms
        barns_in_farms = db.query(Barn).filter(Barn.farm_id.in_(accessible_farm_ids)).all()
        barn_ids = [b.id for b in barns_in_farms]
        total_checklists = db.query(Checklist).filter(Checklist.barn_id.in_(barn_ids)).count() if barn_ids else 0
        unresolved_incidents = db.query(Incident).filter(
            Incident.barn_id.in_(barn_ids),
            Incident.resolved == False
        ).count() if barn_ids else 0
        
        return {
            "total_barns": total_barns,
            "high_risk_barns": high_risk_barns,
            "total_checklists": total_checklists,
            "unresolved_incidents": unresolved_incidents
        }
    finally:
        db.close()
