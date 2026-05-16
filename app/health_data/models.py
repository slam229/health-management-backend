import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Date, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.common.database import Base


class HealthProfile(Base):
    """健康画像表 - 用户静态健康信息"""
    __tablename__ = "health_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    gender = Column(String(8), nullable=True)  # male/female
    birth_date = Column(Date, nullable=True)
    height_cm = Column(Numeric(5, 1), nullable=True)
    weight_kg = Column(Numeric(5, 1), nullable=True)
    chronic_diseases = Column(JSONB, default=list)  # ["hypertension", "diabetes"]
    family_history = Column(JSONB, default=list)  # ["father:hypertension"]
    allergies = Column(JSONB, default=list)  # 过敏史
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="health_profile")


class HealthRecord(Base):
    """健康数据记录表 - 每次采集的指标快照"""
    __tablename__ = "health_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    source = Column(String(32), nullable=False)  # manual/ocr/wearable
    metrics = Column(JSONB, nullable=False)  # 各项健康指标
    recorded_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="health_records")

    # Indexes
    __table_args__ = (
        {"schema": None},
    )
