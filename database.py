import os
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, User, Farm, Barn, Checklist, Incident, Visitor, Alert
from datetime import datetime, timedelta
import bcrypt
import random

@st.cache_resource
def get_engine():
    """Get or create database engine (cached)"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        st.error("⚠️ Database connection not configured. Please set the DATABASE_URL environment variable in Replit Secrets.")
        st.stop()
    
    return create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=5,
        max_overflow=10,
        connect_args={
            "sslmode": "require",
            "connect_timeout": 10,
        }
    )

def get_session_factory():
    """Get session factory"""
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Initialize database tables"""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """Get database session"""
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        return db
    finally:
        pass

def get_user_assigned_farms(user_id: int, db: Session):
    """Get list of farm IDs assigned to a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return []
    return [farm.id for farm in user.assigned_farms]

def can_access_all_farms(role: str) -> bool:
    """Check if user role can access all farms (admin and auditor)"""
    return role in ["admin", "auditor"]

def get_accessible_farm_ids(user_id: int, user_role: str, db: Session):
    """Get list of farm IDs accessible to the user based on their role"""
    if can_access_all_farms(user_role):
        # Admin and auditor can see all farms
        farms = db.query(Farm).all()
        return [farm.id for farm in farms]
    else:
        # Other users can only see assigned farms
        return get_user_assigned_farms(user_id, db)

def assign_user_to_farm(user_id: int, farm_id: int, db: Session):
    """Assign a user to a farm"""
    user = db.query(User).filter(User.id == user_id).first()
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    
    if user and farm:
        if farm not in user.assigned_farms:
            user.assigned_farms.append(farm)
            db.commit()
            return True
    return False

def unassign_user_from_farm(user_id: int, farm_id: int, db: Session):
    """Remove a user's assignment from a farm"""
    user = db.query(User).filter(User.id == user_id).first()
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    
    if user and farm:
        if farm in user.assigned_farms:
            user.assigned_farms.remove(farm)
            db.commit()
            return True
    return False

def create_demo_data():
    """Create demo users and sample data"""
    db = get_db()
    
    try:
        # Check if demo users already exist
        if db.query(User).filter(User.email == "admin@farmtwin.com").first():
            return
        
        # Create demo users
        demo_users = [
            {"name": "Admin User", "email": "admin@farmtwin.com", "password": "admin123", "role": "admin"},
            {"name": "Farm Manager", "email": "manager@farmtwin.com", "password": "manager123", "role": "manager"},
            {"name": "Farm Worker", "email": "worker@farmtwin.com", "password": "worker123", "role": "worker"},
            {"name": "Farm Visitor", "email": "visitor@farmtwin.com", "password": "visitor123", "role": "visitor"},
            {"name": "Veterinarian", "email": "vet@farmtwin.com", "password": "vet123", "role": "vet"},
            {"name": "Auditor", "email": "auditor@farmtwin.com", "password": "auditor123", "role": "auditor"},
        ]
        
        for user_data in demo_users:
            password_hash = bcrypt.hashpw(user_data["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user = User(
                name=user_data["name"],
                email=user_data["email"],
                password_hash=password_hash,
                role=user_data["role"]
            )
            db.add(user)
        
        # Create demo farms
        farm1 = Farm(
            name="Green Valley Farm",
            location="California, USA",
            description="Premium livestock farm with modern facilities"
        )
        db.add(farm1)
        
        farm2 = Farm(
            name="Sunny Hills Ranch",
            location="Texas, USA",
            description="Large-scale cattle and poultry operation"
        )
        db.add(farm2)
        
        db.commit()
        db.refresh(farm1)
        db.refresh(farm2)
        
        if farm1.id is None or farm2.id is None:
            raise ValueError("Failed to create farms")
        
        # Assign users to farms (worker, visitor, vet to farm1; manager to both)
        manager = db.query(User).filter(User.role == "manager").first()
        worker = db.query(User).filter(User.role == "worker").first()
        visitor = db.query(User).filter(User.role == "visitor").first()
        vet = db.query(User).filter(User.role == "vet").first()
        
        if manager:
            manager.assigned_farms.extend([farm1, farm2])
        if worker:
            worker.assigned_farms.append(farm1)
        if visitor:
            visitor.assigned_farms.append(farm1)
        if vet:
            vet.assigned_farms.append(farm1)
        
        db.commit()
        
        # Create demo barns for farm1
        barn_configs_f1 = [
            {"name": "Barn A", "capacity": 100, "x": 0, "y": 0, "z": 0, "farm_id": farm1.id},
            {"name": "Barn B", "capacity": 150, "x": 50, "y": 0, "z": 0, "farm_id": farm1.id},
            {"name": "Barn C", "capacity": 120, "x": 0, "y": 50, "z": 0, "farm_id": farm1.id},
        ]
        
        # Create demo barns for farm2
        barn_configs_f2 = [
            {"name": "Barn X", "capacity": 200, "x": 0, "y": 0, "z": 0, "farm_id": farm2.id},
            {"name": "Barn Y", "capacity": 180, "x": 50, "y": 0, "z": 0, "farm_id": farm2.id},
        ]
        
        for config in barn_configs_f1 + barn_configs_f2:
            barn = Barn(
                farm_id=config["farm_id"],
                name=config["name"],
                capacity=config["capacity"],
                position_x=config["x"],
                position_y=config["y"],
                position_z=config["z"],
                risk_level=random.choice(["low", "medium", "high"])
            )
            db.add(barn)
        
        db.commit()
        
        # Create sample checklists
        if worker is None or worker.id is None:
            raise ValueError("Worker user not found")
            
        # Get barns only from farm1 (since worker is assigned to farm1)
        barns = db.query(Barn).filter(Barn.farm_id == farm1.id).all()
        
        for i in range(10):
            barn = random.choice(barns)
            checklist = Checklist(
                barn_id=barn.id,
                user_id=worker.id,
                hygiene_score=random.randint(6, 10),
                mortality_count=random.randint(0, 3),
                feed_quality=random.randint(7, 10),
                water_quality=random.randint(8, 10),
                ventilation_score=random.randint(6, 9),
                temperature=random.uniform(18, 25),
                humidity=random.uniform(45, 65),
                notes=f"Daily inspection {i+1}",
                gps_lat=37.7749 + random.uniform(-0.01, 0.01),
                gps_lng=-122.4194 + random.uniform(-0.01, 0.01),
                submitted_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            db.add(checklist)
        
        # Create sample incidents
        for i in range(3):
            barn = random.choice(barns)
            incident = Incident(
                barn_id=barn.id,
                user_id=worker.id,
                incident_type=random.choice(["disease", "equipment_failure", "environmental"]),
                severity=random.choice(["low", "medium", "high"]),
                description=f"Sample incident {i+1}",
                actions_taken="Immediate response taken",
                resolved=random.choice([True, False]),
                reported_at=datetime.utcnow() - timedelta(days=random.randint(0, 7))
            )
            db.add(incident)
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        print(f"Error creating demo data: {e}")
    finally:
        db.close()
