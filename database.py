import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, User, Farm, Barn, Checklist, Incident, Visitor, Alert
from datetime import datetime, timedelta
import bcrypt
import random

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/farmtwin")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass

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
        
        # Create demo farm
        farm = Farm(
            name="Green Valley Farm",
            location="California, USA",
            description="Premium livestock farm with modern facilities"
        )
        db.add(farm)
        db.commit()
        
        # Create demo barns
        barn_configs = [
            {"name": "Barn A", "capacity": 100, "x": 0, "y": 0, "z": 0},
            {"name": "Barn B", "capacity": 150, "x": 50, "y": 0, "z": 0},
            {"name": "Barn C", "capacity": 120, "x": 0, "y": 50, "z": 0},
            {"name": "Barn D", "capacity": 80, "x": 50, "y": 50, "z": 0},
        ]
        
        for config in barn_configs:
            barn = Barn(
                farm_id=farm.id,
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
        worker = db.query(User).filter(User.role == "worker").first()
        barns = db.query(Barn).all()
        
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
