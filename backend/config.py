"""
Configuration management using pydantic-settings.
Loads environment variables from .env file.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str
    supervisor_model: str = "gpt-4o"
    content_model: str = "gpt-4o-mini"
    chat_agent_model: str = "gpt-4o-mini"

    # TTS Configuration
    voice_alex: str = "alloy"
    voice_mira: str = "onyx"
    tts_model: str = "tts-1"
    tts_speed: float = 1.0  # Speech speed (0.25 to 4.0, 1.0 = default)

    # Dust Configuration
    dust_api_key: str
    dust_workspace_id: str

    # Server Configuration
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    frontend_url: str = "http://localhost:5173"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Feature Flags
    enable_chat_agents: bool = True
    enable_dust: bool = False
    enable_transcription: bool = True
    chat_agent_count: int = 3

    # Podcast Configuration
    podcast_turn_duration: int = 20
    transition_sound_enabled: bool = True
    chat_agent_interval: int = 15

    # Scoring Configuration
    vote_weight: int = 1
    thumbs_up_weight: int = 5
    thumbs_down_weight: int = -3
    topic_continuation_threshold: float = 0.7

    # Development
    debug: bool = True
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global settings instance
settings = Settings()
