"""
Server-Sent Events (SSE) streaming endpoint.
"""
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from backend.core.state import get_state
from backend.utils.logger import setup_logger
import asyncio
import json

router = APIRouter(prefix="/api", tags=["streaming"])
logger = setup_logger(__name__)


@router.get("/stream")
async def stream_events():
    """
    SSE endpoint for real-time updates.

    Streams events:
    - TOPICS_UPDATED: When topics/votes change
    - NOW_PLAYING: When podcast segment starts playing
    - TRANSCRIPT_UPDATE: When new dialogue is added
    - CHAT_MESSAGE: When new chat message arrives
    """
    state = await get_state()

    # Create queue for this client
    client_queue = asyncio.Queue()
    state.add_sse_client(client_queue)

    logger.info("New SSE client connected")

    async def event_generator():
        """Generate SSE events from the queue."""
        try:
            while True:
                # Wait for event from queue
                event = await client_queue.get()

                # Format as SSE event
                event_type = event.get("event", "message")
                event_data = event.get("data", {})

                # Yield SSE formatted event
                yield {
                    "event": event_type,
                    "data": json.dumps(event_data)
                }

        except asyncio.CancelledError:
            logger.info("SSE client disconnected")
        finally:
            # Clean up when client disconnects
            state.remove_sse_client(client_queue)

    return EventSourceResponse(event_generator())
