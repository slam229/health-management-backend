from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from typing import List

from app.common.database import get_db
from app.auth.utils import decode_token
from app.auth.models import User
from app.auth.router import get_current_user
from app.monitoring.models import AnomalyAlert
from app.monitoring.schemas import AnomalyAlertResponse
from app.monitoring.ws_manager import ws_manager

router = APIRouter(prefix="/monitoring", tags=["监测告警"])


@router.websocket("/ws/alerts/{user_id}")
async def websocket_alerts(
    websocket: WebSocket,
    user_id: str,
    token: str = Query(...)
):
    """WebSocket告警推送"""
    payload = decode_token(token)
    if not payload or payload.get("sub") != user_id:
        await websocket.close(code=4001)
        return
    
    await ws_manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(user_id, websocket)


@router.get("/alerts/history", response_model=List[AnomalyAlertResponse])
async def get_alert_history(
    skip: int = 0,
    limit: int = 20,
    is_read: bool = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取告警历史"""
    query = select(AnomalyAlert).where(AnomalyAlert.user_id == current_user.id)
    
    if is_read is not None:
        query = query.where(AnomalyAlert.is_read == is_read)
    
    query = query.order_by(AnomalyAlert.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/alerts/{alert_id}/read")
async def mark_alert_read(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """标记告警为已读"""
    result = await db.execute(select(AnomalyAlert).where(AnomalyAlert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        return {"success": False, "message": "告警不存在"}
    
    alert.is_read = True
    await db.commit()
    return {"success": True}


@router.post("/alerts/read-all")
async def mark_all_alerts_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """标记所有告警为已读"""
    result = await db.execute(
        select(AnomalyAlert).where(
            AnomalyAlert.user_id == current_user.id,
            AnomalyAlert.is_read == False
        )
    )
    alerts = result.scalars().all()
    for alert in alerts:
        alert.is_read = True
    await db.commit()
    return {"success": True, "count": len(alerts)}


@router.get("/alerts/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取未读告警数量"""
    result = await db.execute(
        select(func.count(AnomalyAlert.id)).where(
            AnomalyAlert.user_id == current_user.id,
            AnomalyAlert.is_read == False
        )
    )
    count = result.scalar()
    return {"unread_count": count}
