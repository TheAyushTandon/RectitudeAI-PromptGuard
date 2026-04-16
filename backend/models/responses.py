"""Response schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ToolCall(BaseModel):
    """Tool call schema."""
    
    tool_name: str = Field(..., description="Name of the tool")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    signature: Optional[str] = Field(None, description="HMAC signature")


class InferenceResponse(BaseModel):
    """Response schema for LLM inference."""
    
    response: str = Field(..., description="LLM generated response")
    tool_calls: List[ToolCall] = Field(default_factory=list, description="Tool calls made by LLM")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    request_id: str = Field(..., description="Unique request identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "The capital of France is Paris.",
                "tool_calls": [],
                "metadata": {
                    "model": "gpt-4",
                    "tokens_used": 45,
                    "latency_ms": 234
                },
                "request_id": "req_789",
                "timestamp": "2026-02-13T10:30:00Z"
            }
        }


class TokenResponse(BaseModel):
    """JWT token response."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")


class ServiceNode(BaseModel):
    """Infrastructure service node information."""
    name: str = Field(..., description="Name of the service node")
    status: str = Field(..., description="Current status of the node (ACTIVE, LIMITED, DOWN)")
    latency: str = Field(..., description="Current latency string (e.g. '12ms')")
    region: str = Field(..., description="deployment region")
    icon_type: str = Field("Activity", description="Icon identifier for the UI")


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    components: Dict[str, str] = Field(default_factory=dict, description="Component status summary")
    infrastructure: List[ServiceNode] = Field(default_factory=list, description="Detailed infrastructure status")


class ErrorResponse(BaseModel):
    """Error response schema."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    request_id: Optional[str] = Field(None, description="Request identifier")


class AgentChatResponse(BaseModel):
    """Response schema for agent-routed chat."""
    
    response: str = Field(..., description="Agent-generated response")
    agent_used: str = Field(..., description="Name of the agent that handled the request")
    request_id: str = Field(..., description="Unique request identifier")
    session_id: str = Field("", description="Session identifier")
    tools_invoked: List[str] = Field(default_factory=list, description="Tools used by the agent")
    capability_token_issued: bool = Field(False, description="Whether a capability token was issued")
    security_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Security pipeline metadata (risk score, decisions, ASI)"
    )
    execution_time_ms: float = Field(0.0, description="Total execution time")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

