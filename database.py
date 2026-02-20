import os
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from models import Base, User, Farm, Barn, Checklist, Incident, Visitor, Alert
import bcrypt


# =========================
# DATABASE ENGINE
# =========================

@st.cache_resource
def get_engine():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        database_url = "sqlite:///farmtwin.db"

    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    else:
        connect_args = {
            "sslmode": "require",
            "connect_timeout": 10,
        }

    return create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args=connect_args
    )


def get_session_factory():
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    migrate_schema()


def get_db() -> Session:
    SessionLocal = get_session_factory()
    return SessionLocal()


# =========================
# SCHEMA MIGRATION
# =========================

def migrate_schema():
    engine = get_engine()
    with engine.connect() as conn:

        def add_column(table, column_def):
            try:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column_def}"))
            except:
                pass

        add_column("checklists", "approved BOOLEAN DEFAULT 0")
        add_column("checklists", "approved_by INTEGER")
        add_column("checklists", "approved_at DATETIME")

        add_column("incidents", "approved BOOLEAN DEFAULT 0")
        add_column("incidents", "approved_by INTEGER")
        add_column("incidents", "approved_at DATETIME")


# =========================
# ACCESS CONTROL
# =========================

def get_user_assigned_farms(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []
    return [farm.id for farm in user.assigned_farms]


def can_access_all_farms(role: str) -> bool:
    return role in ["admin", "auditor"]


def get_accessible_farm_ids(user_id: int, user_role: str, db: Session):
    if can_access_all_farms(user_role):
        farms = db.query(Farm).all()
        return [farm.id for farm in farms]
    return get_user_assigned_farms(user_id, db)


# =========================
# USER ↔ FARM ASSIGNMENT
# =========================

def assign_user_to_farm(user_id: int, farm_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    farm = db.query(Farm).filter(Farm.id == farm_id).first()

    if user and farm:
        if farm not in user.assigned_farms:
            user.assigned_farms.append(farm)
            db.commit()
            return True
    return False


def unassign_user_from_farm(user_id: int, farm_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    farm = db.query(Farm).filter(Farm.id == farm_id).first()

    if user and farm:
        if farm in user.assigned_farms:
            user.assigned_farms.remove(farm)
            db.commit()
            return True
    return False


# =========================
# DEMO USERS (LOGIN FIX)
# =========================

def create_demo_data():
    db = get_db()

    try:
        demo_users = [
            {"name": "Admin User", "email": "admin@farmtwin.com", "password": "admin123", "role": "admin"},
            {"name": "Farm Manager", "email": "manager@farmtwin.com", "password": "manager123", "role": "manager"},
            {"name": "Farm Worker", "email": "worker@farmtwin.com", "password": "worker123", "role": "worker"},
            {"name": "Farm Visitor", "email": "visitor@farmtwin.com", "password": "visitor123", "role": "visitor"},
            {"name": "Veterinarian", "email": "vet@farmtwin.com", "password": "vet123", "role": "vet"},
            {"name": "Auditor", "email": "auditor@farmtwin.com", "password": "auditor123", "role": "auditor"},
        ]

        for data in demo_users:
            existing = db.query(User).filter(User.email == data["email"]).first()

            new_hash = bcrypt.hashpw(
                data["password"].encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            if existing:
                existing.password_hash = new_hash
                existing.role = data["role"]
                existing.is_active = True
            else:
                user = User(
                    name=data["name"],
                    email=data["email"],
                    password_hash=new_hash,
                    role=data["role"],
                    is_active=True
                )
                db.add(user)

        db.commit()

    except Exception as e:
        db.rollback()
        print("Demo setup error:", e)

    finally:
        db.close()