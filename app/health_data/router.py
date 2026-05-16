from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List, Optional

from app.common.database import get_db
from app.auth.router import get_current_user
from app.auth.models import User
from app.health_data.models import HealthProfile, HealthRecord
from app.health_data.schemas import (
    HealthProfileCreate, HealthProfileUpdate, HealthProfileResponse,
    HealthRecordCreate, HealthRecordResponse, WearableDataInput
)
from app.health_data.services import HealthDataService
from app.monitoring.services import AnomalyDetectionService

router = APIRouter(prefix="/health", tags=["健康数据"])

anomaly_service = AnomalyDetectionService()


# ===== 健康画像接口 =====

@router.post("/profile", response_model=HealthProfileResponse)
async def create_or_update_profile(
    profile_data: HealthProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建或更新用户健康画像"""
    result = await db.execute(
        select(HealthProfile).where(HealthProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if profile:
        # 更新
        for key, value in profile_data.model_dump(exclude_unset=True).items():
            setattr(profile, key, value)
    else:
        # 创建
        profile = HealthProfile(
            user_id=current_user.id,
            **profile_data.model_dump()
        )
        db.add(profile)
    
    await db.commit()
    await db.refresh(profile)
    return profile


@router.get("/profile", response_model=HealthProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户健康画像"""
    result = await db.execute(
        select(HealthProfile).where(HealthProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="健康画像不存在")
    return profile


# ===== 健康数据记录接口 =====

@router.post("/record/manual", response_model=HealthRecordResponse)
async def create_manual_record(
    record_data: HealthRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """手动录入健康数据"""
    metrics = record_data.model_dump(exclude_none=True)
    if "recorded_at" not in metrics:
        metrics["recorded_at"] = record_data.recorded_at
    
    record = HealthRecord(
        user_id=current_user.id,
        source="manual",
        metrics=metrics
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    
    # 触发异常检测
    await anomaly_service.check_and_create_alerts(current_user.id, metrics, db)
    
    return record


@router.post("/record/ocr", response_model=HealthRecordResponse)
async def upload_ocr_record(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """上传体检报告图片进行OCR识别"""
    # 保存上传的文件
    contents = await file.read()
    file_id = f"{current_user.id}_{file.filename}"
    # TODO: 上传到MinIO或本地存储
    image_url = f"/uploads/ocr/{file_id}"
    
    # OCR识别
    extracted_metrics = await HealthDataService.ocr_extract_health_data(image_url)
    
    # 创建健康记录
    record = HealthRecord(
        user_id=current_user.id,
        source="ocr",
        metrics=extracted_metrics
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    
    # 触发异常检测
    await anomaly_service.check_and_create_alerts(current_user.id, extracted_metrics, db)
    
    return record


@router.post("/record/wearable", response_model=HealthRecordResponse)
async def sync_wearable_data(
    wearable_data: WearableDataInput,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """同步可穿戴设备数据"""
    # 标准化数据
    standardized_metrics = HealthDataService.standardize_wearable_data(
        wearable_data.device_type,
        wearable_data.metrics
    )
    
    record = HealthRecord(
        user_id=current_user.id,
        source="wearable",
        metrics=standardized_metrics,
        recorded_at=wearable_data.recorded_at
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    
    # 触发异常检测
    await anomaly_service.check_and_create_alerts(current_user.id, standardized_metrics, db)
    
    return record


@router.get("/records", response_model=List[HealthRecordResponse])
async def get_records(
    skip: int = 0,
    limit: int = 20,
    source: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取健康记录列表"""
    query = select(HealthRecord).where(HealthRecord.user_id == current_user.id)
    if source:
        query = query.where(HealthRecord.source == source)
    query = query.order_by(HealthRecord.recorded_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()
