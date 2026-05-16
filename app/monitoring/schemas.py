from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional


class AnomalyAlertResponse(BaseModel):
    id: UUID
    user_id: UUID
    alert_type: str
    severity: str
    metric_name: str
    metric_value: str
    threshold_value: str
    title: str
    description: Optional[str] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AlertThresholdConfig(BaseModel):
    """告警阈值配置"""
    blood_pressure_sys: float = 140.0  # 收缩压
    blood_pressure_dia: float = 90.0   # 舒张压
    fasting_glucose: float = 7.0        # 空腹血糖 (mmol/L)
    uric_acid: float = 420.0           # 尿酸 (μmol/L)
    cholesterol_total: float = 5.7     # 总胆固醇 (mmol/L)
    heart_rate_high: int = 100         # 心率上限
    heart_rate_low: int = 50           # 心率下限
    weight_gain_rate: float = 5.0      # 体重增长百分比警告
