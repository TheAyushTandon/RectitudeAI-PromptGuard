from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any

from backend.layer5_orchestration.orchestrator import _audit
from backend.gateway.config import settings

router = APIRouter()

class ThresholdSettings(BaseModel):
    prefilter_instant_block: float
    prefilter_escalate: float
    ml_block_threshold: float
    ml_escalate_threshold: float
    asi_alert_threshold: float

@router.get("/v1/dashboard/stats")
async def get_dashboard_stats():
    """Get aggregated stats for dashboard cards"""
    return _audit.get_stats()

@router.get("/v1/dashboard/logs")
async def get_dashboard_logs(limit: int = 50):
    """Get real-time streaming audit logs for datatable"""
    return _audit.get_logs(limit=limit)

@router.get("/v1/dashboard/settings", response_model=ThresholdSettings)
async def get_dashboard_settings():
    """Get current threshold settings"""
    return ThresholdSettings(
        prefilter_instant_block=settings.prefilter_instant_block,
        prefilter_escalate=settings.prefilter_escalate,
        ml_block_threshold=settings.ml_block_threshold,
        ml_escalate_threshold=settings.ml_escalate_threshold,
        asi_alert_threshold=settings.asi_alert_threshold
    )

@router.post("/v1/dashboard/settings")
async def update_dashboard_settings(new_settings: ThresholdSettings):
    """Update threshold settings dynamically and persist them."""
    settings.prefilter_instant_block = new_settings.prefilter_instant_block
    settings.prefilter_escalate = new_settings.prefilter_escalate
    settings.ml_block_threshold = new_settings.ml_block_threshold
    settings.ml_escalate_threshold = new_settings.ml_escalate_threshold
    settings.asi_alert_threshold = new_settings.asi_alert_threshold
    
    # Persist to disk
    _audit.save_settings(new_settings.dict())
    
    return {"status": "success", "settings": new_settings.dict()}
