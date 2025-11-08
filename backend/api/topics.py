"""
Topic API endpoints.
"""
from fastapi import APIRouter, HTTPException
from backend.models import (
    Topic,
    TopicCreate,
    VoteRequest,
    ReactionRequest,
    TopicSuggestionsRequest,
    TopicSuggestion
)
from backend.core.state import get_state
from backend.utils.logger import setup_logger
from backend.config import settings
from typing import List
from openai import AsyncOpenAI

router = APIRouter(prefix="/api", tags=["topics"])
logger = setup_logger(__name__)
client = AsyncOpenAI(api_key=settings.openai_api_key)


@router.post("/topic", response_model=Topic)
async def create_topic(topic_data: TopicCreate):
    """
    Create a new topic for voting.

    Args:
        topic_data: Topic creation request

    Returns:
        Created topic
    """
    logger.info(f"Creating topic: {topic_data.text}")

    state = await get_state()

    # Create topic
    topic = Topic(
        text=topic_data.text,
        nickname=topic_data.nickname
    )

    # Add to state
    state.add_topic(topic)

    # Broadcast update
    await state.broadcast_event("TOPICS_UPDATED", {
        "topics": [t.model_dump() for t in state.get_sorted_topics()]
    })

    logger.info(f"Topic created: {topic.id}")

    return topic


@router.post("/vote")
async def vote_on_topic(vote_data: VoteRequest):
    """
    Vote on a topic.

    Args:
        vote_data: Vote request with topic ID and delta

    Returns:
        Updated topic
    """
    logger.info(f"Vote on topic {vote_data.id}: {vote_data.delta}")

    state = await get_state()

    # Vote
    topic = state.vote_topic(vote_data.id, vote_data.delta)

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Broadcast update
    await state.broadcast_event("TOPICS_UPDATED", {
        "topics": [t.model_dump() for t in state.get_sorted_topics()]
    })

    return topic


@router.post("/react")
async def react_to_topic(reaction_data: ReactionRequest):
    """
    Add emoji reaction to topic.

    Args:
        reaction_data: Reaction request with topic ID and emoji

    Returns:
        Updated topic
    """
    logger.info(f"Reaction on topic {reaction_data.id}: {reaction_data.emoji}")

    # Validate emoji
    if reaction_data.emoji not in ["👍", "👎"]:
        raise HTTPException(status_code=400, detail="Invalid emoji. Use 👍 or 👎")

    state = await get_state()

    # React
    topic = state.react_topic(reaction_data.id, reaction_data.emoji)

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Broadcast update
    await state.broadcast_event("TOPICS_UPDATED", {
        "topics": [t.model_dump() for t in state.get_sorted_topics()]
    })

    return topic


@router.get("/topics", response_model=List[Topic])
async def get_topics():
    """
    Get all topics sorted by score.

    Returns:
        List of topics
    """
    state = await get_state()
    return state.get_sorted_topics()


@router.post("/topics/suggestions", response_model=List[TopicSuggestion])
async def generate_topic_suggestions(request: TopicSuggestionsRequest):
    """
    Generate AI topic suggestions based on chat messages.

    Args:
        request: Chat messages to analyze

    Returns:
        List of suggested topics
    """
    logger.info(f"Generating topic suggestions from {len(request.messages)} messages")

    if not request.messages:
        return []

    # Format chat messages for the AI
    chat_context = "\n".join([
        f"{msg.sender}: {msg.text}"
        for msg in request.messages
    ])

    # Create prompt for topic generation
    prompt = f"""Based on this conversation, suggest 3 interesting podcast topics that the AI hosts Alex and Mira could discuss.

Conversation:
{chat_context}

Generate exactly 3 diverse and engaging topics. For each topic provide:
1. A catchy title (5-10 words)
2. A brief description (1-2 sentences)

Format your response as JSON array:
[
  {{"id": 1, "title": "...", "description": "...", "votes": 0}},
  {{"id": 2, "title": "...", "description": "...", "votes": 0}},
  {{"id": 3, "title": "...", "description": "...", "votes": 0}}
]"""

    try:
        # Call OpenAI to generate suggestions
        response = await client.chat.completions.create(
            model=settings.content_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a creative podcast producer who generates interesting discussion topics."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8,
            response_format={"type": "json_object"}
        )

        # Parse response
        import json
        result = json.loads(response.choices[0].message.content)

        # Handle both array and object with array responses
        if isinstance(result, list):
            suggestions = result
        elif isinstance(result, dict):
            # Try different possible keys
            suggestions = result.get("topics") or result.get("podcast_topics") or result.get("suggestions") or []
        else:
            logger.error(f"Unexpected response format: {result}")
            suggestions = []

        # Validate and return
        validated_suggestions = [
            TopicSuggestion(**suggestion)
            for suggestion in suggestions[:3]  # Max 3 suggestions
        ]

        logger.info(f"Generated {len(validated_suggestions)} topic suggestions")
        return validated_suggestions

    except Exception as e:
        logger.error(f"Error generating topic suggestions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate topic suggestions: {str(e)}"
        )
