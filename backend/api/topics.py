"""
Topic API endpoints.
"""
from fastapi import APIRouter, HTTPException
from backend.models import Topic, TopicCreate, VoteRequest, ReactionRequest
from backend.core.state import get_state
from backend.utils.logger import setup_logger
from typing import List

router = APIRouter(prefix="/api", tags=["topics"])
logger = setup_logger(__name__)


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
