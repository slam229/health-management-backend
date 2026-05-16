from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime

from app.monitoring.models import AnomalyAlert
from app.monitoring.schemas import AlertThresholdConfig
from app.monitoring.ws_manager import ws_manager


class AnomalyDetectionService:
    """异常检测引擎"""
    
    # 告警规则配置
    ALERT_RULES = {
        "blood_pressure_sys": {
            "display_name": "收缩压",
            "unit": "mmHg",
            "critical": 180,
            "warning": 140,
            "type": "blood_pressure"
        },
        "blood_pressure_dia": {
            "display_name": "舒张压",
            "unit": "mmHg",
            "critical": 110,
            "warning": 90,
            "type": "blood_pressure"
        },
        "fasting_glucose": {
            "display_name": "空腹血糖",
            "unit": "mmol/L",
            "critical": 11.1,
            "warning": 7.0,
            "type": "glucose"
        },
        "uric_acid": {
            "display_name": "尿酸",
            "unit": "μmol/L",
            "critical": 550,
            "warning": 420,
            "type": "uric_acid"
        },
        "heart_rate": {
            "display_name": "心率",
            "unit": "bpm",
            "critical_high": 120,
            "critical_low": 40,
            "warning_high": 100,
            "warning_low": 50,
            "type": "heart_rate"
        }
    }

    async def check_and_create_alerts(
        self, 
        user_id, 
        metrics: Dict[str, Any], 
        db: AsyncSession
    ) -> List[AnomalyAlert]:
        """检测异常并创建告警"""
        alerts = []
        
        for metric_key, metric_value in metrics.items():
            if metric_key not in self.ALERT_RULES or metric_value is None:
                continue
            
            rule = self.ALERT_RULES[metric_key]
            
            # 判断是否异常
            is_anomaly = False
            severity = "warning"
            threshold = 0
            
            if "critical" in rule:
                if metric_value >= rule["critical"]:
                    is_anomaly = True
                    severity = "critical"
                    threshold = rule["critical"]
                elif metric_value >= rule["warning"]:
                    is_anomaly = True
                    severity = "warning"
                    threshold = rule["warning"]
            elif "critical_high" in rule:
                if metric_value >= rule["critical_high"] or metric_value <= rule["critical_low"]:
                    is_anomaly = True
                    severity = "critical"
                    threshold = rule["critical_high"]
                elif metric_value >= rule["warning_high"] or metric_value <= rule["warning_low"]:
                    is_anomaly = True
                    severity = "warning"
                    threshold = rule["warning_high"]
            
            if is_anomaly:
                # 生成告警
                alert = await self._create_alert(
                    user_id=user_id,
                    alert_type=rule["type"],
                    severity=severity,
                    metric_name=metric_key,
                    metric_value=metric_value,
                    threshold=threshold,
                    display_name=rule["display_name"],
                    unit=rule["unit"],
                    db=db
                )
                alerts.append(alert)
                
                # WebSocket推送
                await ws_manager.send_personal_message(
                    str(user_id),
                    {
                        "type": "anomaly_alert",
                        "data": {
                            "id": str(alert.id),
                            "alert_type": alert.alert_type,
                            "severity": alert.severity,
                            "title": alert.title,
                            "description": alert.description,
                            "created_at": alert.created_at.isoformat()
                        }
                    }
                )
        
        return alerts

    async def _create_alert(
        self,
        user_id,
        alert_type: str,
        severity: str,
        metric_name: str,
        metric_value: float,
        threshold: float,
        display_name: str,
        unit: str,
        db: AsyncSession
    ) -> AnomalyAlert:
        """创建告警记录"""
        alert = AnomalyAlert(
            user_id=user_id,
            alert_type=alert_type,
            severity=severity,
            metric_name=metric_name,
            metric_value=str(metric_value),
            threshold_value=str(threshold),
            title=f"{display_name}异常",
            description=f"您的{display_name}为 {metric_value}{unit}，超过安全阈值 {threshold}{unit}",
            is_read=False
        )
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        return alert
