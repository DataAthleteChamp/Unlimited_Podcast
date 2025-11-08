"""
Pydantic models for the Endless AI Podcast API.
"""
from backend.models.topic import (
    Topic,
    TopicCreate,
    VoteRequest,
    ReactionRequest,
    TopicSuggestionsRequest,
    TopicSuggestion,
    ChatMessageForSuggestion
)
from backend.models.podcast import (
    DialogueSegment,
    PodcastTurn,
    NowPlaying,
    TranscriptEntry,
    PodcastStatus
)
from backend.models.chat import ChatMessage, ChatMessageCreate, ChatAgentPersona

__all__ = [
    # Topic models
    "Topic",
    "TopicCreate",
    "VoteRequest",
    "ReactionRequest",
    "TopicSuggestionsRequest",
    "TopicSuggestion",
    "ChatMessageForSuggestion",
    # Podcast models
    "DialogueSegment",
    "PodcastTurn",
    "NowPlaying",
    "TranscriptEntry",
    "PodcastStatus",
    # Chat models
    "ChatMessage",
    "ChatMessageCreate",
    "ChatAgentPersona",
]
