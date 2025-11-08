"""
Chat-related Pydantic models.
"""
from pydantic import BaseModel, Field
from typing import Optional
import time
import uuid


class ChatMessage(BaseModel):
    """Chat message model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nickname: str = Field(..., min_length=1, max_length=50)
    message: str = Field(..., min_length=1, max_length=500)
    is_ai: bool = Field(default=False, description="Whether message is from AI agent")
    persona: Optional[str] = Field(None, description="AI persona if is_ai=True")
    timestamp: float = Field(default_factory=time.time)


class ChatMessageCreate(BaseModel):
    """Request model for creating a chat message."""
    nickname: str = Field(..., min_length=1, max_length=50)
    message: str = Field(..., min_length=1, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "nickname": "PodcastFan123",
                "message": "Great discussion!"
            }
        }


class ChatAgentPersona(BaseModel):
    """AI chat agent persona configuration."""
    name: str
    personality: str
    system_prompt: str
    emoji: str = "🤖"
