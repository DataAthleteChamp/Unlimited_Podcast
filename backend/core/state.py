"""
In-memory state management for the podcast application.

This module manages all application state including topics, podcast status,
chat messages, and transcript. No database is used - everything is in memory.
"""
from typing import List, Optional, Dict
from backend.models import Topic, ChatMessage, TranscriptEntry, PodcastTurn
import asyncio
import time


class AppState:
    """
    Global application state manager.

    Singleton pattern - use get_instance() to access.
    """

    _instance: Optional['AppState'] = None
    _lock: asyncio.Lock = asyncio.Lock()

    def __init__(self):
        """Initialize empty state."""
        # Topics
        self.topics: List[Topic] = []

        # Podcast state
        self.podcast_running: bool = False
        self.current_topic_id: Optional[str] = None
        self.current_topic_text: str = ""  # Text of current topic being discussed
        self.turn_number: int = 0
        self.current_speaker: str = "Alex"  # Alternates between Alex and Mira
        self.last_turn_summary: str = ""
        self.podcast_started_at: Optional[float] = None

        # Queue-based podcast system
        self.topic_queue: List[str] = []  # Queue of topic IDs (FIFO)
        self.used_topics: set = set()  # Topics already discussed (don't repeat)

        # Podcast history
        self.turns_history: List[PodcastTurn] = []
        self.transcript: List[TranscriptEntry] = []

        # Chat messages
        self.chat_messages: List[ChatMessage] = []

        # SSE clients (for broadcasting)
        self.sse_clients: List[asyncio.Queue] = []

    @classmethod
    async def get_instance(cls) -> 'AppState':
        """Get singleton instance of AppState."""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    # ===== Topic Management =====

    def add_topic(self, topic: Topic) -> Topic:
        """Add a new topic to the list."""
        self.topics.append(topic)
        return topic

    def get_topic_by_id(self, topic_id: str) -> Optional[Topic]:
        """Get topic by ID."""
        for topic in self.topics:
            if topic.id == topic_id:
                return topic
        return None

    def vote_topic(self, topic_id: str, delta: int) -> Optional[Topic]:
        """
        Vote on a topic.

        Args:
            topic_id: Topic ID
            delta: Vote delta (1 for upvote, -1 for downvote)

        Returns:
            Updated topic or None if not found
        """
        topic = self.get_topic_by_id(topic_id)
        if topic:
            topic.votes += delta
        return topic

    def react_topic(self, topic_id: str, emoji: str) -> Optional[Topic]:
        """
        Add emoji reaction to topic.

        Args:
            topic_id: Topic ID
            emoji: Emoji reaction (👍 or 👎)

        Returns:
            Updated topic or None if not found
        """
        topic = self.get_topic_by_id(topic_id)
        if not topic:
            return None

        if emoji == "👍":
            topic.reactions_thumbs_up += 1
        elif emoji == "👎":
            topic.reactions_thumbs_down += 1

        return topic

    def get_top_topic(self) -> Optional[Topic]:
        """
        Get highest-scored topic.

        Returns:
            Topic with highest score, or None if no topics
        """
        if not self.topics:
            return None

        return max(self.topics, key=lambda t: t.score)

    def get_sorted_topics(self) -> List[Topic]:
        """Get all topics sorted by score (highest first)."""
        return sorted(self.topics, key=lambda t: t.score, reverse=True)

    # ===== Queue Management =====

    def add_to_queue(self, topic_id: str) -> int:
        """
        Add topic to the podcast queue.

        Args:
            topic_id: Topic ID to add

        Returns:
            Position in queue (1-indexed)
        """
        # Don't add if already in queue or already used
        if topic_id in self.topic_queue or topic_id in self.used_topics:
            return -1

        self.topic_queue.append(topic_id)
        return len(self.topic_queue)

    def get_next_from_queue(self) -> Optional[Topic]:
        """
        Get next topic from queue (FIFO).

        Returns:
            Next topic to discuss, or None if queue is empty
        """
        # Try to get from queue first
        if self.topic_queue:
            topic_id = self.topic_queue.pop(0)  # FIFO
            topic = self.get_topic_by_id(topic_id)
            if topic:
                return topic

        # Fallback: Get highest-voted unused topic
        unused_topics = [
            t for t in self.topics
            if t.id not in self.used_topics
        ]

        if not unused_topics:
            # All topics used, reset
            self.used_topics.clear()
            unused_topics = self.topics

        if unused_topics:
            return max(unused_topics, key=lambda t: t.score)

        return None

    def mark_topic_used(self, topic_id: str):
        """Mark topic as discussed (won't be repeated)."""
        self.used_topics.add(topic_id)

    def get_queue_info(self) -> Dict:
        """
        Get information about the current queue.

        Returns:
            Dictionary with queue information
        """
        queue_topics = []
        for topic_id in self.topic_queue:
            topic = self.get_topic_by_id(topic_id)
            if topic:
                queue_topics.append({
                    "id": topic.id,
                    "text": topic.text,
                    "votes": topic.votes
                })

        return {
            "current_topic": self.current_topic_text,
            "queue": queue_topics,
            "queue_length": len(self.topic_queue),
            "used_count": len(self.used_topics)
        }

    def clear_queue(self):
        """Clear the entire queue."""
        self.topic_queue.clear()

    # ===== Podcast Control =====

    def start_podcast(self):
        """Start the podcast."""
        self.podcast_running = True
        self.podcast_started_at = time.time()
        self.turn_number = 0

    def stop_podcast(self):
        """Stop the podcast."""
        self.podcast_running = False
        self.current_topic_id = None
        self.current_speaker = "Alex"

    def get_podcast_uptime(self) -> float:
        """Get podcast uptime in seconds."""
        if not self.podcast_started_at:
            return 0.0
        return time.time() - self.podcast_started_at

    def toggle_speaker(self):
        """Toggle between Alex and Mira."""
        self.current_speaker = "Mira" if self.current_speaker == "Alex" else "Alex"

    def should_continue_topic(self, topic: Topic) -> bool:
        """
        Decide if current topic should continue based on positive reactions.

        Args:
            topic: Topic to evaluate

        Returns:
            True if should continue, False if should switch
        """
        from backend.config import settings

        total_reactions = topic.reactions_thumbs_up + topic.reactions_thumbs_down

        # Not enough data to decide
        if total_reactions < 10:
            return False

        return topic.positive_ratio >= settings.topic_continuation_threshold

    # ===== Transcript Management =====

    def add_transcript_entry(self, entry: TranscriptEntry):
        """Add entry to transcript."""
        self.transcript.append(entry)

        # Keep only last 50 entries for memory efficiency
        if len(self.transcript) > 50:
            self.transcript = self.transcript[-50:]

    def get_recent_transcript(self, count: int = 10) -> List[TranscriptEntry]:
        """Get recent transcript entries."""
        return self.transcript[-count:]

    def clear_transcript(self):
        """Clear transcript (used when starting new topic)."""
        self.transcript.clear()

    # ===== Chat Management =====

    def add_chat_message(self, message: ChatMessage) -> ChatMessage:
        """Add chat message."""
        self.chat_messages.append(message)

        # Keep only last 100 messages
        if len(self.chat_messages) > 100:
            self.chat_messages = self.chat_messages[-100:]

        return message

    def get_recent_chat_messages(self, count: int = 50) -> List[ChatMessage]:
        """Get recent chat messages."""
        return self.chat_messages[-count:]

    # ===== Turn History =====

    def add_turn(self, turn: PodcastTurn):
        """Add completed turn to history."""
        self.turns_history.append(turn)
        self.turn_number += 1
        self.last_turn_summary = turn.summary

        # Keep only last 20 turns
        if len(self.turns_history) > 20:
            self.turns_history = self.turns_history[-20:]

    def get_recent_turns(self, count: int = 5) -> List[PodcastTurn]:
        """Get recent turns."""
        return self.turns_history[-count:]

    def get_current_now_playing(self) -> Optional[Dict]:
        """
        Get current now playing information.
        
        Returns:
            Dictionary with now playing info or None if nothing is playing
        """
        if not self.turns_history:
            return None
        
        # Get the most recent turn
        last_turn = self.turns_history[-1]
        
        # Determine which speaker is currently active based on current_speaker
        # For now, return the last speaker from the most recent turn
        # In a real implementation, you'd track which segment is currently playing
        if self.current_speaker == "Alex":
            return {
                "speaker": "Alex",
                "text": last_turn.alex.text,
                "audio_url": last_turn.alex.audio_url,
                "topic_id": last_turn.topic_id,
                "topic_text": last_turn.topic_text,
                "turn_number": last_turn.turn_number
            }
        else:
            return {
                "speaker": "Mira",
                "text": last_turn.mira.text,
                "audio_url": last_turn.mira.audio_url,
                "topic_id": last_turn.topic_id,
                "topic_text": last_turn.topic_text,
                "turn_number": last_turn.turn_number
            }

    # ===== SSE Client Management =====

    def add_sse_client(self, queue: asyncio.Queue):
        """Register new SSE client."""
        self.sse_clients.append(queue)

    def remove_sse_client(self, queue: asyncio.Queue):
        """Unregister SSE client."""
        if queue in self.sse_clients:
            self.sse_clients.remove(queue)

    async def broadcast_event(self, event_type: str, data: Dict):
        """
        Broadcast SSE event to all connected clients.

        Args:
            event_type: Event type (e.g., "TOPICS_UPDATED")
            data: Event data dictionary
        """
        event = {"event": event_type, "data": data}

        # Send to all connected clients
        for client_queue in self.sse_clients:
            try:
                await client_queue.put(event)
            except Exception:
                # If client is disconnected, remove it
                self.remove_sse_client(client_queue)

    # ===== Utility Methods =====

    def reset_state(self):
        """Reset all state (useful for testing)."""
        self.topics.clear()
        self.podcast_running = False
        self.current_topic_id = None
        self.current_topic_text = ""
        self.turn_number = 0
        self.current_speaker = "Alex"
        self.last_turn_summary = ""
        self.podcast_started_at = None
        self.topic_queue.clear()
        self.used_topics.clear()
        self.turns_history.clear()
        self.transcript.clear()
        self.chat_messages.clear()


# Global state instance accessor
async def get_state() -> AppState:
    """Get global application state."""
    return await AppState.get_instance()
