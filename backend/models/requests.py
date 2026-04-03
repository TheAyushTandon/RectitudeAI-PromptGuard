"""Request schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ToolCallRequest(BaseModel):
    name: str = Field(..., description="Tool name")
    params: Dict[str, Any] = Field(default_factory=dict)


class InferenceRequest(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    prompt: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[str] = Field(None, description="Session ID for multi-turn tracking")
    max_tokens: Optional[int] = Field(1000, ge=1, le=4096)
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    tool_calls: Optional[List[ToolCallRequest]] = Field(
        None, description="Tool calls the LLM is requesting"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "prompt": "What is the capital of France?",
                "conversation_id": "conv_456",
                "max_tokens": 500,
                "temperature": 0.7,
            }
        }


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
