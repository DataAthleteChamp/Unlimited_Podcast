"""
Podcast control API endpoints.
"""
from fastapi import APIRouter
from backend.models import PodcastStatus, TranscriptEntry, NowPlaying
from backend.core.state import get_state
from backend.core.scheduler import podcast_scheduler
from backend.utils.logger import setup_logger
from typing import List, Optional
import time

router = APIRouter(prefix="/api/podcast", tags=["podcast"])
logger = setup_logger(__name__)


@router.post("/start")
async def start_podcast():
    """
    Start the podcast scheduler.

    Returns:
        Status message
    """
    logger.info("Starting podcast via API")

    await podcast_scheduler.start()

    return {"status": "started", "message": "Podcast started successfully"}


@router.post("/stop")
async def stop_podcast():
    """
    Stop the podcast scheduler.

    Returns:
        Status message
    """
    logger.info("Stopping podcast via API")

    await podcast_scheduler.stop()

    return {"status": "stopped", "message": "Podcast stopped successfully"}


@router.get("/status", response_model=PodcastStatus)
async def get_podcast_status():
    """
    Get current podcast status.

    Returns:
        Podcast status
    """
    state = await get_state()

    current_topic_text = None
    if state.current_topic_id:
        current_topic = state.get_topic_by_id(state.current_topic_id)
        if current_topic:
            current_topic_text = current_topic.text

    return PodcastStatus(
        running=state.podcast_running,
        current_topic=current_topic_text,
        turn_count=state.turn_number,
        uptime_seconds=state.get_podcast_uptime()
    )


@router.get("/transcript", response_model=List[TranscriptEntry])
async def get_transcript():
    """
    Get recent transcript entries.

    Returns:
        List of transcript entries
    """
    state = await get_state()
    return state.get_recent_transcript(count=20)


@router.get("/now", response_model=Optional[NowPlaying])
async def get_now_playing():
    """
    Get current now playing information.

    Returns:
        Current now playing info or None if nothing is playing
    """
    state = await get_state()
    
    now_playing_data = state.get_current_now_playing()
    if not now_playing_data:
        return None
    
    # Calculate approximate timing (you may want to track this more accurately)
    current_time = time.time()
    
    return NowPlaying(
        topic_id=now_playing_data["topic_id"],
        topic_text=now_playing_data["topic_text"],
        speaker=now_playing_data["speaker"],
        text=now_playing_data["text"],
        audio_url=now_playing_data["audio_url"],
        started_at=current_time - 5,  # Approximate - you may want to track this better
        ends_at=current_time + 10,    # Approximate - you may want to track this better
        turn_number=now_playing_data["turn_number"]
    )
