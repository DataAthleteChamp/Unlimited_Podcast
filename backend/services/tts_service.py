"""
Text-to-Speech Service using OpenAI TTS API.

Converts dialogue text into spoken audio with different voices for Alex and Mira.
"""
from openai import AsyncOpenAI
from backend.config import settings
from backend.utils.logger import setup_logger
from pathlib import Path
import time
import os

logger = setup_logger(__name__)


class TTSService:
    """
    Text-to-Speech service for converting dialogue to audio.

    Uses OpenAI TTS API with streaming support.
    """

    def __init__(self):
        """Initialize OpenAI client and audio directory."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.tts_model
        self.speed = settings.tts_speed

        # Audio storage directory
        self.audio_dir = Path("backend/static/audio")
        self.audio_dir.mkdir(parents=True, exist_ok=True)

        # Voice mapping
        self.voices = {
            "Alex": settings.voice_alex,
            "Mira": settings.voice_mira
        }

    async def generate_speech(
        self,
        text: str,
        speaker: str
    ) -> str:
        """
        Generate speech audio from text.

        Args:
            text: Text to convert to speech
            speaker: Speaker name ('Alex' or 'Mira')

        Returns:
            Relative URL to the generated audio file
        """
        logger.info(f"Generating speech for {speaker}: {len(text)} characters")

        # Get voice for speaker
        voice = self.voices.get(speaker, settings.voice_alex)

        # Generate unique filename
        timestamp = int(time.time() * 1000)
        filename = f"{speaker.lower()}_{timestamp}.mp3"
        file_path = self.audio_dir / filename

        try:
            # Stream audio to file
            async with self.client.audio.speech.with_streaming_response.create(
                model=self.model,
                voice=voice,
                input=text,
                response_format="mp3",
                speed=self.speed
            ) as response:
                await response.stream_to_file(file_path)

            logger.info(f"Generated audio: {filename}")

            # Return URL path (relative to static directory)
            return f"/static/audio/{filename}"

        except Exception as e:
            logger.error(f"TTS generation failed for {speaker}: {e}", exc_info=True)
            raise

    async def cleanup_old_files(self, max_age_seconds: int = 3600):
        """
        Clean up audio files older than max_age_seconds.

        Args:
            max_age_seconds: Maximum age in seconds (default: 1 hour)
        """
        current_time = time.time()
        deleted_count = 0

        for audio_file in self.audio_dir.glob("*.mp3"):
            # Check file age
            file_age = current_time - audio_file.stat().st_mtime

            if file_age > max_age_seconds:
                try:
                    audio_file.unlink()
                    deleted_count += 1
                    logger.debug(f"Deleted old audio file: {audio_file.name}")
                except Exception as e:
                    logger.error(f"Failed to delete {audio_file.name}: {e}")

        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old audio files")


# Global TTS service instance
tts_service = TTSService()
