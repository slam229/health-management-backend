from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime, date
from typing import Optional, List, Dict, Any


class HealthProfileCreate(BaseModel):
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    chronic_diseases: List[str] = []
    family_history: List[str] = []
    allergies: List[str] = []


class HealthProfileUpdate(BaseModel):
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    chronic_diseases: Optional[List[str]] = None
    family_history: Optional[List[str]] = None
    allergies: Optional[List[str]] = None


class HealthProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    chronic_diseases: List[str] = []
    family_history: List[str] = []
    allergies: List[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HealthRecordCreate(BaseModel):
    """手动录入健康数据"""
    blood_pressure_sys: Optional[float] = None  # 收缩压
    blood_pressure_dia: Optional[float] = None  # 舒张压
    fasting_glucose: Optional[float] = None   # 空腹血糖 (mmol/L)
    uric_acid: Optional[float] = None          # 尿酸 (μmol/L)
    cholesterol_total: Optional[float] = None  # 总胆固醇
    heart_rate: Optional[int] = None           # 心率
    weight: Optional[float] = None             # 当前体重
    recorded_at: Optional[datetime] = None


class WearableDataInput(BaseModel):
    """可穿戴设备上传数据"""
    device_type: str = Field(..., description="设备类型: smartwatch/band")
    metrics: Dict[str, Any] = Field(..., description="设备采集的指标")
    recorded_at: datetime


class HealthRecordResponse(BaseModel):
    id: UUID
    user_id: UUID
    source: str
    metrics: Dict[str, Any]
    recorded_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
