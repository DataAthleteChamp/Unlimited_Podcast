"""
Podcast-related Pydantic models.
"""
from pydantic import BaseModel, Field
from typing import Optional
import time


class DialogueSegment(BaseModel):
    """A single dialogue segment from one speaker."""
    speaker: str = Field(..., description="Speaker name: 'Alex' or 'Mira'")
    text: str = Field(..., description="Dialogue text")
    audio_url: Optional[str] = Field(None, description="URL to audio file")


class PodcastTurn(BaseModel):
    """Complete podcast turn with both speakers."""
    topic_id: str
    topic_text: str
    alex: DialogueSegment
    mira: DialogueSegment
    summary: str = Field(..., description="Brief summary of this turn")
    turn_number: int = Field(..., description="Turn number in sequence")
    created_at: float = Field(default_factory=time.time)


class NowPlaying(BaseModel):
    """Currently playing podcast information."""
    topic_id: str
    topic_text: str
    speaker: str = Field(..., description="Current speaker: 'Alex' or 'Mira'")
    text: str = Field(..., description="Current dialogue text")
    audio_url: str = Field(..., description="URL to current audio segment")
    started_at: float
    ends_at: float
    turn_number: int


class TranscriptEntry(BaseModel):
    """Single transcript entry."""
    speaker: str
    text: str
    timestamp: float = Field(default_factory=time.time)
    turn_number: int


class PodcastStatus(BaseModel):
    """Podcast status response."""
    running: bool
    current_topic: Optional[str] = None
    turn_count: int = 0
    uptime_seconds: float = 0.0
