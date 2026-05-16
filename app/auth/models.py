import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.common.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(128), unique=True, nullable=True, index=True)
    password_hash = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    health_profile = relationship("HealthProfile", back_populates="user", uselist=False)
    health_records = relationship("HealthRecord", back_populates="user")
    risk_assessments = relationship("RiskAssessment", back_populates="user")
    health_plans = relationship("HealthPlan", back_populates="user")
    plan_executions = relationship("PlanExecution", back_populates="user")
    mirror_tasks = relationship("MirrorTask", back_populates="user")
    anomaly_alerts = relationship("AnomalyAlert", back_populates="user")
