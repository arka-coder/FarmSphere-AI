
"""
FarmSphere AI — Database Models (SQLAlchemy)
Supports SQLite (dev, zero-install) and PostgreSQL (production).
"""
from datetime import datetime
from typing import Optional
import json

from sqlalchemy import (
    create_engine, Column, String, Float, Integer,
    Boolean, DateTime, Text, JSON, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session

from config import settings

# ── Engine — handles SQLite and PostgreSQL transparently ─────────────────────

_is_sqlite = settings.database_url.startswith("sqlite")

if _is_sqlite:
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ── Models ──────────────────────────────────────────────────────────────────

class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(String, primary_key=True)
    name = Column(String(200), nullable=False)
    phone = Column(String(20), unique=True, nullable=True)
    location = Column(String(200), nullable=True)
    district = Column(String(100), nullable=True)
    state_name = Column(String(100), nullable=True)
    land_size_acres = Column(Float, nullable=True)
    preferred_language = Column(String(10), default="en")
    primary_crop = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    conversations = relationship("ConversationRecord", back_populates="farmer")
    disease_records = relationship("DiseaseRecord", back_populates="farmer")
    alert_logs = relationship("AlertLog", back_populates="farmer")


class ConversationRecord(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    farmer_id = Column(String, ForeignKey("farmers.id"), nullable=False)
    session_id = Column(String, index=True)
    user_message = Column(Text)
    assistant_response = Column(Text)
    intent = Column(String(100), nullable=True)
    language = Column(String(10), default="en")
    agents_invoked = Column(JSON, default=list)
    latency_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("Farmer", back_populates="conversations")


class DiseaseRecord(Base):
    __tablename__ = "disease_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    farmer_id = Column(String, ForeignKey("farmers.id"), nullable=False)
    crop_type = Column(String(100))
    disease_name = Column(String(200))
    confidence_score = Column(Float)
    severity = Column(String(50))
    symptoms = Column(JSON, default=list)
    alternatives = Column(JSON, default=list)
    treatment_given = Column(JSON, default=dict)
    image_path = Column(String(500), nullable=True)
    hitl_required = Column(Boolean, default=False)
    outcome = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("Farmer", back_populates="disease_records")


class AlertLog(Base):
    __tablename__ = "alert_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    farmer_id = Column(String, ForeignKey("farmers.id"), nullable=True)
    alert_type = Column(String(100))    # weather | disease | pest | market
    severity = Column(String(50))       # low | medium | high | critical
    title = Column(String(300))
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("Farmer", back_populates="alert_logs")


class AgentMetrics(Base):
    __tablename__ = "agent_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, index=True)
    agent_name = Column(String(100))
    duration_ms = Column(Float)
    status = Column(String(50))
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CropCalendarEntry(Base):
    __tablename__ = "crop_calendar"

    id = Column(Integer, primary_key=True, autoincrement=True)
    farmer_id = Column(String, ForeignKey("farmers.id"), nullable=False)
    crop_type = Column(String(100))
    season = Column(String(50))
    task_name = Column(String(200))
    task_type = Column(String(100))   # sowing | irrigation | fertilizer | harvest
    scheduled_date = Column(DateTime)
    completed = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ── Database Helpers ─────────────────────────────────────────────────────────

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)
