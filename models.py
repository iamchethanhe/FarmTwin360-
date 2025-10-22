from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # admin, manager, worker, visitor, vet, auditor
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Farm(Base):
    __tablename__ = "farms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(200))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Barn(Base):
    __tablename__ = "barns"
    
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    name = Column(String(100), nullable=False)
    capacity = Column(Integer)
    position_x = Column(Float, default=0)
    position_y = Column(Float, default=0)
    position_z = Column(Float, default=0)
    risk_level = Column(String(10), default="low")  # high, medium, low
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    farm = relationship("Farm")

class Checklist(Base):
    __tablename__ = "checklists"
    
    id = Column(Integer, primary_key=True, index=True)
    barn_id = Column(Integer, ForeignKey("barns.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    hygiene_score = Column(Integer)  # 1-10
    mortality_count = Column(Integer, default=0)
    feed_quality = Column(Integer)  # 1-10
    water_quality = Column(Integer)  # 1-10
    ventilation_score = Column(Integer)  # 1-10
    temperature = Column(Float)
    humidity = Column(Float)
    notes = Column(Text)
    gps_lat = Column(Float)
    gps_lng = Column(Float)
    photo_path = Column(String(500))
    submitted_at = Column(DateTime, default=datetime.utcnow)
    
    barn = relationship("Barn")
    user = relationship("User")

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    barn_id = Column(Integer, ForeignKey("barns.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    incident_type = Column(String(50))  # disease, equipment_failure, etc.
    severity = Column(String(10))  # high, medium, low
    description = Column(Text)
    actions_taken = Column(Text)
    photo_path = Column(String(500))
    resolved = Column(Boolean, default=False)
    reported_at = Column(DateTime, default=datetime.utcnow)
    
    barn = relationship("Barn")
    user = relationship("User")

class Visitor(Base):
    __tablename__ = "visitors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    company = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    purpose = Column(String(200))
    qr_code = Column(String(100), unique=True)
    check_in_time = Column(DateTime)
    check_out_time = Column(DateTime)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    
    farm = relationship("Farm")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50))  # missed_checklist, high_risk, incident
    message = Column(Text)
    severity = Column(String(10))  # high, medium, low
    barn_id = Column(Integer, ForeignKey("barns.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    barn = relationship("Barn")
    user = relationship("User")
