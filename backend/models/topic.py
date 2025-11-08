"""
Topic-related Pydantic models.
"""
from pydantic import BaseModel, Field
from typing import Optional
import time
import uuid


class TopicCreate(BaseModel):
    """Request model for creating a new topic."""
    text: str = Field(..., min_length=1, max_length=200, description="Topic text")
    nickname: Optional[str] = Field(None, max_length=50, description="User nickname")


class Topic(BaseModel):
    """Topic model with voting and reaction data."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    nickname: Optional[str] = None
    votes: int = 0
    reactions_thumbs_up: int = 0
    reactions_thumbs_down: int = 0
    created_at: float = Field(default_factory=time.time)

    @property
    def score(self) -> float:
        """
        Calculate weighted score for topic prioritization.

        Formula: votes * VOTE_WEIGHT + thumbs_up * THUMBS_UP_WEIGHT + thumbs_down * THUMBS_DOWN_WEIGHT
        """
        from backend.config import settings

        base_score = self.votes * settings.vote_weight
        positive_boost = self.reactions_thumbs_up * settings.thumbs_up_weight
        negative_penalty = self.reactions_thumbs_down * abs(settings.thumbs_down_weight)

        total_score = base_score + positive_boost - negative_penalty

        # Recency bonus (decay over 1 hour)
        age_seconds = time.time() - self.created_at
        recency_multiplier = max(0.5, 1.0 - (age_seconds / 3600))

        return total_score * recency_multiplier

    @property
    def positive_ratio(self) -> float:
        """Calculate ratio of positive reactions."""
        total_reactions = self.reactions_thumbs_up + self.reactions_thumbs_down
        if total_reactions == 0:
            return 0.0
        return self.reactions_thumbs_up / total_reactions


class VoteRequest(BaseModel):
    """Request model for voting on a topic."""
    id: str = Field(..., description="Topic ID")
    delta: int = Field(..., description="Vote delta: 1 for upvote, -1 for downvote")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "delta": 1
            }
        }


class ReactionRequest(BaseModel):
    """Request model for emoji reactions."""
    id: str = Field(..., description="Topic ID")
    emoji: str = Field(..., description="Emoji: 👍 or 👎")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "emoji": "👍"
            }
        }


class ChatMessageForSuggestion(BaseModel):
    """Chat message for topic suggestions."""
    text: str
    sender: str
    timestamp: str


class TopicSuggestionsRequest(BaseModel):
    """Request model for generating topic suggestions from chat."""
    messages: list[ChatMessageForSuggestion]


class TopicSuggestion(BaseModel):
    """AI-generated topic suggestion."""
    id: int
    title: str
    description: str
    votes: int = 0
