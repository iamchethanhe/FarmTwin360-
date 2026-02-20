from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import jwt
import bcrypt
import sys
import os

# Add parent directory to path to import existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db, get_accessible_farm_ids
from models import User, Farm, Barn, Checklist, Incident, Visitor, Alert
from sqlalchemy.orm import Session

app = FastAPI(title="FarmTwin360 Mobile API")
security = HTTPBearer()

SECRET_KEY = os.getenv("SESSION_SECRET", "farmtwin-secret-key-change-in-production")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    token: str
    user: dict

class ChecklistCreate(BaseModel):
    barn_id: int
    hygiene_score: int
    mortality_count: int
    feed_quality: int
    water_quality: int
    ventilation_score: int
    temperature: float
    humidity: float
    notes: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None

class IncidentCreate(BaseModel):
    barn_id: int
    incident_type: str
    severity: str
    description: str
    actions_taken: Optional[str] = None

# Helper functions
def create_jwt_token(user_id: int, role: str) -> str:
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_jwt_token(token)
    return payload

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# API Endpoints
@app.post("/api/auth/login", response_model=LoginResponse)
def login(request: LoginRequest):
    db = get_db()
    try:
        user = db.query(User).filter(User.email == request.email, User.is_active == True).first()
        if not user or not verify_password(request.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        token = create_jwt_token(user.id, user.role)
        return {
            "token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            }
        }
    finally:
        db.close()

@app.get("/api/user/profile")
def get_profile(current_user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        user = db.query(User).filter(User.id == current_user['user_id']).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    finally:
        db.close()

@app.get("/api/farms")
def get_farms(current_user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        farm_ids = get_accessible_farm_ids(current_user['user_id'], current_user['role'], db)
        farms = db.query(Farm).filter(Farm.id.in_(farm_ids)).all()
        return [{
            "id": f.id,
            "name": f.name,
            "location": f.location,
            "description": f.description
        } for f in farms]
    finally:
        db.close()

@app.get("/api/farms/{farm_id}/barns")
def get_barns(farm_id: int, current_user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        farm_ids = get_accessible_farm_ids(current_user['user_id'], current_user['role'], db)
        if farm_id not in farm_ids:
            raise HTTPException(status_code=403, detail="Access denied")
        
        barns = db.query(Barn).filter(Barn.farm_id == farm_id).all()
        return [{
            "id": b.id,
            "name": b.name,
            "capacity": b.capacity,
            "risk_level": b.risk_level
        } for b in barns]
    finally:
        db.close()

@app.post("/api/checklists")
def create_checklist(data: ChecklistCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        # Create checklist
        checklist = Checklist(
            barn_id=data.barn_id,
            user_id=current_user['user_id'],
            hygiene_score=data.hygiene_score,
            mortality_count=data.mortality_count,
            feed_quality=data.feed_quality,
            water_quality=data.water_quality,
            ventilation_score=data.ventilation_score,
            temperature=data.temperature,
            humidity=data.humidity,
            notes=data.notes,
            gps_lat=data.gps_lat,
            gps_lng=data.gps_lng,
            submitted_at=datetime.utcnow()
        )
        db.add(checklist)
        db.commit()
        db.refresh(checklist)
        
        # Get user and barn info for notification
        user = db.query(User).filter(User.id == current_user['user_id']).first()
        barn = db.query(Barn).filter(Barn.id == data.barn_id).first()
        
        print(f"\n[NOTIFICATION DEBUG] Creating notifications for checklist:")
        print(f"  - Checklist ID: {checklist.id}")
        print(f"  - Reporter: {user.name} (ID: {user.id})")
        print(f"  - Barn: {barn.name}")
        
        # Create notifications for managers and admins
        notification_users = db.query(User).filter(
            User.role.in_(['admin', 'manager']),
            User.is_active == True
        ).all()
        
        print(f"  - Found {len(notification_users)} users to notify")
        
        for notif_user in notification_users:
            print(f"  - Creating notification for {notif_user.name} (Role: {notif_user.role})")
            alert = Alert(
                type="checklist_submitted",
                message=f"New checklist submitted by {user.name} for {barn.name} - ⏳ PENDING REVIEW",
                severity="low",
                barn_id=barn.id,
                user_id=notif_user.id,
                read=False,
                created_at=datetime.utcnow()
            )
            db.add(alert)
        
        db.commit()
        print(f"  ✓ All notifications committed to database\n")
        return {"id": checklist.id, "message": "Checklist created successfully"}
    finally:
        db.close()

@app.get("/api/checklists")
def get_checklists(current_user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        farm_ids = get_accessible_farm_ids(current_user['user_id'], current_user['role'], db)
        checklists = db.query(Checklist).join(Barn).filter(Barn.farm_id.in_(farm_ids)).order_by(Checklist.submitted_at.desc()).limit(50).all()
        
        return [{
            "id": c.id,
            "barn_name": c.barn.name,
            "hygiene_score": c.hygiene_score,
            "mortality_count": c.mortality_count,
            "temperature": c.temperature,
            "humidity": c.humidity,
            "submitted_at": c.submitted_at.isoformat(),
            "approved": c.approved
        } for c in checklists]
    finally:
        db.close()

@app.post("/api/incidents")
def create_incident(data: IncidentCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        # Create incident
        incident = Incident(
            barn_id=data.barn_id,
            user_id=current_user['user_id'],
            incident_type=data.incident_type,
            severity=data.severity,
            description=data.description,
            actions_taken=data.actions_taken,
            reported_at=datetime.utcnow()
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)
        
        # Get user and barn info for notification
        user = db.query(User).filter(User.id == current_user['user_id']).first()
        barn = db.query(Barn).filter(Barn.id == data.barn_id).first()
        
        print(f"\n[NOTIFICATION DEBUG] Creating notifications for incident:")
        print(f"  - Incident ID: {incident.id}")
        print(f"  - Reporter: {user.name} (ID: {user.id})")
        print(f"  - Barn: {barn.name}")
        print(f"  - Severity: {data.severity}")
        print(f"  - Type: {data.incident_type}")
        
        # Determine notification severity based on incident severity
        alert_severity = data.severity  # high, medium, or low
        
        # Create notifications for managers, admins, and vets
        notification_roles = ['admin', 'manager']
        if data.severity == 'high' or data.incident_type == 'disease':
            notification_roles.append('vet')  # Notify vets for high severity or disease
        
        print(f"  - Notifying roles: {notification_roles}")
        
        notification_users = db.query(User).filter(
            User.role.in_(notification_roles),
            User.is_active == True
        ).all()
        
        print(f"  - Found {len(notification_users)} users to notify")
        
        for notif_user in notification_users:
            print(f"  - Creating notification for {notif_user.name} (Role: {notif_user.role}, ID: {notif_user.id})")
            alert = Alert(
                type="incident_reported",
                message=f"🚨 {data.severity.upper()} incident reported by {user.name} at {barn.name}: {data.incident_type} - ⚠️ PENDING APPROVAL",
                severity=alert_severity,
                barn_id=barn.id,
                user_id=notif_user.id,
                read=False,
                created_at=datetime.utcnow()
            )
            db.add(alert)
            print(f"    ✓ Alert added to session")
        
        db.commit()
        print(f"  ✓ All notifications committed to database\n")
        return {"id": incident.id, "message": "Incident reported successfully"}
    finally:
        db.close()

@app.get("/api/incidents")
def get_incidents(current_user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        farm_ids = get_accessible_farm_ids(current_user['user_id'], current_user['role'], db)
        incidents = db.query(Incident).join(Barn).filter(Barn.farm_id.in_(farm_ids)).order_by(Incident.reported_at.desc()).limit(50).all()
        
        return [{
            "id": i.id,
            "barn_name": i.barn.name,
            "incident_type": i.incident_type,
            "severity": i.severity,
            "description": i.description,
            "resolved": i.resolved,
            "reported_at": i.reported_at.isoformat(),
            "approved": i.approved
        } for i in incidents]
    finally:
        db.close()

@app.get("/api/dashboard/stats")
def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        farm_ids = get_accessible_farm_ids(current_user['user_id'], current_user['role'], db)
        
        total_barns = db.query(Barn).filter(Barn.farm_id.in_(farm_ids)).count()
        total_checklists = db.query(Checklist).join(Barn).filter(Barn.farm_id.in_(farm_ids)).count()
        total_incidents = db.query(Incident).join(Barn).filter(Barn.farm_id.in_(farm_ids)).count()
        unresolved_incidents = db.query(Incident).join(Barn).filter(Barn.farm_id.in_(farm_ids), Incident.resolved == False).count()
        
        return {
            "total_farms": len(farm_ids),
            "total_barns": total_barns,
            "total_checklists": total_checklists,
            "total_incidents": total_incidents,
            "unresolved_incidents": unresolved_incidents
        }
    finally:
        db.close()

@app.get("/api/alerts")
def get_alerts(current_user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        alerts = db.query(Alert).filter(Alert.user_id == current_user['user_id'], Alert.read == False).order_by(Alert.created_at.desc()).all()
        
        return [{
            "id": a.id,
            "type": a.type,
            "message": a.message,
            "severity": a.severity,
            "created_at": a.created_at.isoformat()
        } for a in alerts]
    finally:
        db.close()

@app.post("/api/alerts/{alert_id}/mark-read")
def mark_alert_read(alert_id: int, current_user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        alert = db.query(Alert).filter(
            Alert.id == alert_id,
            Alert.user_id == current_user['user_id']
        ).first()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert.read = True
        db.commit()
        return {"message": "Alert marked as read"}
    finally:
        db.close()

@app.post("/api/alerts/mark-all-read")
def mark_all_alerts_read(current_user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        db.query(Alert).filter(
            Alert.user_id == current_user['user_id'],
            Alert.read == False
        ).update({"read": True})
        db.commit()
        return {"message": "All alerts marked as read"}
    finally:
        db.close()

@app.get("/api/notifications/recent")
def get_recent_notifications(limit: int = 20, current_user: dict = Depends(get_current_user)):
    """Get recent notifications (both read and unread)"""
    db = get_db()
    try:
        notifications = db.query(Alert).filter(
            Alert.user_id == current_user['user_id']
        ).order_by(Alert.created_at.desc()).limit(limit).all()
        
        return [{
            "id": n.id,
            "type": n.type,
            "message": n.message,
            "severity": n.severity,
            "read": n.read,
            "created_at": n.created_at.isoformat()
        } for n in notifications]
    finally:
        db.close()

# ===== MANAGER APPROVAL ENDPOINTS =====
@app.get("/api/manager/pending-checklists")
def get_pending_checklists(current_user: dict = Depends(get_current_user)):
    """Get pending checklists for manager approval"""
    if current_user['role'] not in ['manager', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db = get_db()
    try:
        farm_ids = get_accessible_farm_ids(current_user['user_id'], current_user['role'], db)
        pending = db.query(Checklist).join(Barn).filter(
            Barn.farm_id.in_(farm_ids),
            Checklist.approved == False
        ).order_by(Checklist.submitted_at.desc()).all()
        
        return [{
            "id": c.id,
            "barn_name": c.barn.name,
            "user_name": c.user.name,
            "hygiene_score": c.hygiene_score,
            "mortality_count": c.mortality_count,
            "feed_quality": c.feed_quality,
            "water_quality": c.water_quality,
            "ventilation_score": c.ventilation_score,
            "temperature": c.temperature,
            "humidity": c.humidity,
            "notes": c.notes,
            "submitted_at": c.submitted_at.isoformat()
        } for c in pending]
    finally:
        db.close()

@app.get("/api/manager/pending-incidents")
def get_pending_incidents(current_user: dict = Depends(get_current_user)):
    """Get pending incidents for manager approval"""
    if current_user['role'] not in ['manager', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db = get_db()
    try:
        farm_ids = get_accessible_farm_ids(current_user['user_id'], current_user['role'], db)
        pending = db.query(Incident).join(Barn).filter(
            Barn.farm_id.in_(farm_ids),
            Incident.approved == False
        ).order_by(Incident.reported_at.desc()).all()
        
        return [{
            "id": i.id,
            "barn_name": i.barn.name,
            "user_name": i.user.name,
            "incident_type": i.incident_type,
            "severity": i.severity,
            "description": i.description,
            "actions_taken": i.actions_taken,
            "resolved": i.resolved,
            "reported_at": i.reported_at.isoformat()
        } for i in pending]
    finally:
        db.close()

# ===== ADMIN MANAGEMENT ENDPOINTS =====
@app.get("/api/admin/users")
def get_all_users(current_user: dict = Depends(get_current_user)):
    """Get all users (admin only)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db = get_db()
    try:
        users = db.query(User).all()
        return [{
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat()
        } for u in users]
    finally:
        db.close()

@app.get("/api/admin/farms")
def get_all_farms(current_user: dict = Depends(get_current_user)):
    """Get all farms (admin only)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db = get_db()
    try:
        farms = db.query(Farm).all()
        return [{
            "id": f.id,
            "name": f.name,
            "location": f.location,
            "description": f.description,
            "created_at": f.created_at.isoformat()
        } for f in farms]
    finally:
        db.close()

@app.get("/api/admin/farm-assignments")
def get_farm_assignments(current_user: dict = Depends(get_current_user)):
    """Get user-farm assignments (admin only)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db = get_db()
    try:
        users = db.query(User).filter(User.role != 'admin').all()
        assignments = []
        for user in users:
            farm_names = [f.name for f in user.assigned_farms]
            assignments.append({
                "user_id": user.id,
                "user_name": user.name,
                "role": user.role,
                "assigned_farms": farm_names
            })
        return assignments
    finally:
        db.close()

@app.get("/api/admin/barns")
def get_all_barns(current_user: dict = Depends(get_current_user)):
    """Get all barns (admin only)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db = get_db()
    try:
        barns = db.query(Barn).all()
        return [{
            "id": b.id,
            "name": b.name,
            "farm_id": b.farm_id,
            "farm_name": b.farm.name if b.farm else "Unknown",
            "capacity": b.capacity,
            "risk_level": b.risk_level,
            "position": f"({b.position_x}, {b.position_y}, {b.position_z})"
        } for b in barns]
    finally:
        db.close()

@app.get("/api/admin/system-stats")
def get_system_stats(current_user: dict = Depends(get_current_user)):
    """Get system statistics (admin only)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db = get_db()
    try:
        return {
            "total_users": db.query(User).count(),
            "total_farms": db.query(Farm).count(),
            "total_barns": db.query(Barn).count(),
            "total_checklists": db.query(Checklist).count(),
            "total_incidents": db.query(Incident).count(),
            "pending_checklists": db.query(Checklist).filter(Checklist.approved == False).count(),
            "pending_incidents": db.query(Incident).filter(Incident.approved == False).count()
        }
    finally:
        db.close()

@app.post("/api/checklists/{checklist_id}/approve")
def approve_checklist(checklist_id: int, current_user: dict = Depends(get_current_user)):
    """Approve a checklist and notify the worker"""
    db = get_db()
    try:
        # Only managers and admins can approve
        if current_user['role'] not in ['manager', 'admin']:
            raise HTTPException(status_code=403, detail="Not authorized to approve")
        
        checklist = db.query(Checklist).filter(Checklist.id == checklist_id).first()
        if not checklist:
            raise HTTPException(status_code=404, detail="Checklist not found")
        
        # Update approval status
        checklist.approved = True
        checklist.approved_by = current_user['user_id']
        checklist.approved_at = datetime.utcnow()
        
        # Get approver and worker info
        approver = db.query(User).filter(User.id == current_user['user_id']).first()
        worker = db.query(User).filter(User.id == checklist.user_id).first()
        barn = db.query(Barn).filter(Barn.id == checklist.barn_id).first()
        
        # Notify the worker
        if worker:
            alert = Alert(
                type="checklist_approved",
                message=f"✅ Your checklist for {barn.name} has been approved by {approver.name}",
                severity="low",
                barn_id=barn.id,
                user_id=worker.id,
                read=False,
                created_at=datetime.utcnow()
            )
            db.add(alert)
        
        db.commit()
        return {"message": "Checklist approved successfully"}
    finally:
        db.close()

@app.post("/api/incidents/{incident_id}/approve")
def approve_incident(incident_id: int, current_user: dict = Depends(get_current_user)):
    """Approve an incident and notify the worker"""
    db = get_db()
    try:
        # Only managers and admins can approve
        if current_user['role'] not in ['manager', 'admin']:
            raise HTTPException(status_code=403, detail="Not authorized to approve")
        
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        # Update approval status
        incident.approved = True
        incident.approved_by = current_user['user_id']
        incident.approved_at = datetime.utcnow()
        
        # Get approver and worker info
        approver = db.query(User).filter(User.id == current_user['user_id']).first()
        worker = db.query(User).filter(User.id == incident.user_id).first()
        barn = db.query(Barn).filter(Barn.id == incident.barn_id).first()
        
        # Notify the worker
        if worker:
            alert = Alert(
                type="incident_approved",
                message=f"✅ Your {incident.severity} severity incident at {barn.name} has been approved by {approver.name}",
                severity="low",
                barn_id=barn.id,
                user_id=worker.id,
                read=False,
                created_at=datetime.utcnow()
            )
            db.add(alert)
        
        db.commit()
        return {"message": "Incident approved successfully"}
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
