"""Security-related schemas."""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class SecurityDecision(BaseModel):
    """Security layer decision output."""
    
    decision: Literal["allow", "block", "escalate"] = Field(..., description="Security decision")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Risk score")
    reason: Optional[str] = Field(None, description="Decision reason")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "decision": "block",
                "risk_score": 0.89,
                "reason": "High injection risk detected",
                "metadata": {
                    "detector": "injection_classifier",
                    "confidence": 0.95
                },
                "timestamp": "2026-02-13T10:30:00Z"
            }
        }


class AuditLog(BaseModel):
    """Audit log entry."""
    
    event_id: str = Field(..., description="Unique event identifier")
    event_type: str = Field(..., description="Type of event")
    user_id: str = Field(..., description="User identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: dict = Field(default_factory=dict, description="Event details")
    severity: Literal["info", "warning", "critical"] = Field("info", description="Event severity")
