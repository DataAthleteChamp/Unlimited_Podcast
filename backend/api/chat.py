"""
Chat API endpoints.
"""
from fastapi import APIRouter
from backend.models import ChatMessage, ChatMessageCreate
from backend.core.state import get_state
from backend.utils.logger import setup_logger
from typing import List

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = setup_logger(__name__)


@router.post("/message", response_model=ChatMessage)
async def send_chat_message(message_data: ChatMessageCreate):
    """
    Send a chat message (from human user).

    Args:
        message_data: Chat message data

    Returns:
        Created chat message
    """
    logger.info(f"Chat message from {message_data.nickname}: {message_data.message}")

    state = await get_state()

    # Create message
    message = ChatMessage(
        nickname=message_data.nickname,
        message=message_data.message,
        is_ai=False
    )

    # Add to state
    state.add_chat_message(message)

    # Broadcast to all clients
    await state.broadcast_event("CHAT_MESSAGE", {
        "nickname": message.nickname,
        "message": message.message,
        "is_ai": message.is_ai,
        "persona": message.persona,
        "timestamp": message.timestamp
    })

    return message


@router.get("/messages", response_model=List[ChatMessage])
async def get_chat_messages():
    """
    Get recent chat messages.

    Returns:
        List of recent chat messages
    """
    state = await get_state()
    return state.get_recent_chat_messages(count=50)
