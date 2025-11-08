"""
Podcast Scheduler - 20-second Turn Loop

This is the core engine that runs the podcast. Every 20 seconds:
1. Supervisor decides next topic
2. Content Generator creates dialogue
3. TTS generates audio
4. Chat Agents react
5. SSE broadcasts updates
"""
from backend.core.state import get_state
from backend.services.supervisor import supervisor_service
from backend.services.content_generator import content_generator_service
from backend.services.tts_service import tts_service
from backend.services.chat_agents import chat_agent_service
from backend.models import PodcastTurn, DialogueSegment, TranscriptEntry, NowPlaying
from backend.config import settings
from backend.utils.logger import setup_logger
import asyncio
import time

logger = setup_logger(__name__)


class PodcastScheduler:
    """
    Main podcast scheduler that orchestrates the 20-second turn loop.
    """

    def __init__(self):
        """Initialize scheduler."""
        self.running = False
        self.task: asyncio.Task = None
        self.chat_agent_task: asyncio.Task = None

    async def start(self):
        """Start the podcast scheduler."""
        if self.running:
            logger.warning("Scheduler already running")
            return

        logger.info("Starting podcast scheduler")
        self.running = True

        state = await get_state()
        state.start_podcast()

        # Start main podcast loop
        self.task = asyncio.create_task(self._podcast_loop())

        # Start chat agent loop (if enabled)
        if settings.enable_chat_agents:
            self.chat_agent_task = asyncio.create_task(self._chat_agent_loop())

        logger.info("Podcast scheduler started")

    async def stop(self):
        """Stop the podcast scheduler."""
        if not self.running:
            logger.warning("Scheduler not running")
            return

        logger.info("Stopping podcast scheduler")
        self.running = False

        state = await get_state()
        state.stop_podcast()

        # Cancel tasks
        if self.task:
            self.task.cancel()
        if self.chat_agent_task:
            self.chat_agent_task.cancel()

        logger.info("Podcast scheduler stopped")

    async def _podcast_loop(self):
        """Main podcast loop - Queue-based endless podcast."""
        state = await get_state()
        exchanges_per_topic = 3  # Number of Alex/Mira exchanges per topic

        while self.running:
            try:
                # Step 1: Get next topic from queue
                selected_topic = state.get_next_from_queue()

                if not selected_topic:
                    logger.warning("No topics in queue, waiting for votes...")
                    await asyncio.sleep(5)
                    continue

                # Clear transcript for fresh start
                logger.info(f"=== New Topic: {selected_topic.text} ===")
                state.clear_transcript()
                state.current_topic_id = selected_topic.id
                state.current_topic_text = selected_topic.text

                # Broadcast topic change
                await state.broadcast_event("TOPIC_CHANGED", {
                    "topic_id": selected_topic.id,
                    "topic_text": selected_topic.text
                })

                # Do multiple exchanges for this topic
                last_alex = ""
                last_mira = ""

                for exchange_num in range(1, exchanges_per_topic + 1):
                    logger.info(f"=== Exchange {exchange_num}/{exchanges_per_topic} for: {selected_topic.text} ===")

                    # Step 2: Generate dialogue (builds on previous exchanges)
                    dialogue = await content_generator_service.generate_dialogue(
                        topic=selected_topic.text,
                        context=f"This is exchange {exchange_num} of {exchanges_per_topic} on this topic." if exchange_num > 1 else "",
                        turn_number=exchange_num,
                        last_alex_text=last_alex,
                        last_mira_text=last_mira
                    )

                    # Update for next exchange
                    last_alex = dialogue["alex"]
                    last_mira = dialogue["mira"]

                    logger.info(f"Dialogue generated: Alex ({len(dialogue['alex'])} chars), Mira ({len(dialogue['mira'])} chars)")

                    # Step 3: Generate audio for both speakers (parallel)
                    logger.info("Generating audio for both speakers...")

                    alex_audio_task = tts_service.generate_speech(dialogue["alex"], "Alex")
                    mira_audio_task = tts_service.generate_speech(dialogue["mira"], "Mira")

                    results = await asyncio.gather(alex_audio_task, mira_audio_task)
                    alex_audio_url, alex_duration = results[0]
                    mira_audio_url, mira_duration = results[1]

                    logger.info(f"Audio generated: Alex={alex_audio_url} ({alex_duration:.1f}s), Mira={mira_audio_url} ({mira_duration:.1f}s)")

                    # Step 4: Create podcast turn
                    podcast_turn = PodcastTurn(
                        topic_id=selected_topic.id,
                        topic_text=selected_topic.text,
                        alex=DialogueSegment(
                            speaker="Alex",
                            text=dialogue["alex"],
                            audio_url=alex_audio_url
                        ),
                        mira=DialogueSegment(
                            speaker="Mira",
                            text=dialogue["mira"],
                            audio_url=mira_audio_url
                        ),
                        summary=dialogue["summary"],
                        turn_number=exchange_num
                    )

                    # Add to state
                    state.add_turn(podcast_turn)

                    # Add transcript entries
                    state.add_transcript_entry(TranscriptEntry(
                        speaker="Alex",
                        text=dialogue["alex"],
                        turn_number=exchange_num
                    ))
                    state.add_transcript_entry(TranscriptEntry(
                        speaker="Mira",
                        text=dialogue["mira"],
                        turn_number=exchange_num
                    ))

                    # Step 5: Broadcast events - Sequential playback with proper timing

                    # Play Alex first
                    logger.info(f"Playing Alex ({alex_duration:.1f}s)...")
                    await state.broadcast_event("NOW_PLAYING", {
                        "speaker": "Alex",
                        "text": dialogue["alex"],
                        "audio_url": alex_audio_url,
                        "topic_id": selected_topic.id,
                        "topic": selected_topic.text,
                        "turn_number": podcast_turn.turn_number,
                        "duration": alex_duration
                    })

                    await state.broadcast_event("TRANSCRIPT_UPDATE", {
                        "speaker": "Alex",
                        "text": dialogue["alex"],
                        "turn_number": podcast_turn.turn_number
                    })

                    # Wait for Alex's audio to finish, plus small buffer
                    await asyncio.sleep(alex_duration + 0.5)

                    # Now play Mira
                    logger.info(f"Playing Mira ({mira_duration:.1f}s)...")
                    await state.broadcast_event("NOW_PLAYING", {
                        "speaker": "Mira",
                        "text": dialogue["mira"],
                        "audio_url": mira_audio_url,
                        "topic_id": selected_topic.id,
                        "topic": selected_topic.text,
                        "turn_number": podcast_turn.turn_number,
                        "duration": mira_duration
                    })

                    await state.broadcast_event("TRANSCRIPT_UPDATE", {
                        "speaker": "Mira",
                        "text": dialogue["mira"],
                        "turn_number": podcast_turn.turn_number
                    })

                    # Wait for Mira's audio to finish before next exchange
                    await asyncio.sleep(mira_duration + 0.5)

                    # Small pause between exchanges for natural pacing
                    if exchange_num < exchanges_per_topic:
                        logger.info(f"Pausing before exchange {exchange_num + 1}...")
                        await asyncio.sleep(2)  # Brief pause between exchanges

                # All exchanges complete for this topic
                # Mark topic as used (don't repeat)
                state.mark_topic_used(selected_topic.id)
                logger.info(f"Completed all {exchanges_per_topic} exchanges for '{selected_topic.text}'")

                # Step 6: Clean up old audio files periodically
                await tts_service.cleanup_old_files()

                # Small pause before next topic
                logger.info("Topic complete. Moving to next topic in queue...")
                await asyncio.sleep(5)

            except asyncio.CancelledError:
                logger.info("Podcast loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in podcast loop: {e}", exc_info=True)
                await asyncio.sleep(5)  # Wait before retry

    async def _chat_agent_loop(self):
        """Chat agent loop - generates AI comments periodically."""
        state = await get_state()

        # Stagger start times for variety
        await asyncio.sleep(5)

        while self.running:
            try:
                # Only generate if podcast is running
                if not state.podcast_running or not state.turns_history:
                    await asyncio.sleep(10)
                    continue

                # Get recent context
                recent_turn = state.turns_history[-1] if state.turns_history else None
                if not recent_turn:
                    await asyncio.sleep(10)
                    continue

                current_topic = recent_turn.topic_text
                recent_dialogue = f"Alex: {recent_turn.alex.text}\nMira: {recent_turn.mira.text}"

                # Generate 1-2 comments
                num_comments = 1 if state.turn_number % 2 == 0 else 2
                comments = await chat_agent_service.generate_multiple_comments(
                    current_topic=current_topic,
                    recent_dialogue=recent_dialogue,
                    count=num_comments
                )

                # Add to state and broadcast
                for comment in comments:
                    state.add_chat_message(comment)

                    await state.broadcast_event("CHAT_MESSAGE", {
                        "nickname": comment.nickname,
                        "message": comment.message,
                        "is_ai": comment.is_ai,
                        "persona": comment.persona,
                        "timestamp": comment.timestamp
                    })

                    logger.info(f"Chat agent comment: {comment.nickname}: {comment.message}")

                    # Small delay between comments
                    await asyncio.sleep(2)

                # Wait before next batch
                interval = settings.chat_agent_interval + (asyncio.get_event_loop().time() % 5)
                await asyncio.sleep(interval)

            except asyncio.CancelledError:
                logger.info("Chat agent loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in chat agent loop: {e}", exc_info=True)
                await asyncio.sleep(10)


# Global scheduler instance
podcast_scheduler = PodcastScheduler()
