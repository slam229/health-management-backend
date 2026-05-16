import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Date, ForeignKey, Numeric, JSON
from app.common.database import Base


class HealthProfile(Base):
    """健康画像表 - 用户静态健康信息"""
    __tablename__ = "health_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    gender = Column(String(8), nullable=True)  # male/female
    birth_date = Column(Date, nullable=True)
    height_cm = Column(Numeric(5, 1), nullable=True)
    weight_kg = Column(Numeric(5, 1), nullable=True)
    chronic_diseases = Column(JSON, default=list)  # ["hypertension", "diabetes"]
    family_history = Column(JSON, default=list)  # ["father:hypertension"]
    allergies = Column(JSON, default=list)  # 过敏史
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class HealthRecord(Base):
    """健康数据记录表 - 每次采集的指标快照"""
    __tablename__ = "health_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    source = Column(String(32), nullable=False)  # manual/ocr/wearable
    metrics = Column(JSON, nullable=False)  # 各项健康指标
    recorded_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
