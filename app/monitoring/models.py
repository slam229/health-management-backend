import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey
from app.common.database import Base


class AnomalyAlert(Base):
    """异常告警表"""
    __tablename__ = "anomaly_alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    alert_type = Column(String(32), nullable=False)  # blood_pressure/glucose/uric_acid/etc
    severity = Column(String(16), nullable=False)    # warning/critical
    metric_name = Column(String(32), nullable=False)
    metric_value = Column(String(32), nullable=False)
    threshold_value = Column(String(32), nullable=False)
    title = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
