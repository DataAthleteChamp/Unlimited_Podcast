"""
Endless AI Podcast - FastAPI Application

Main application entry point that sets up FastAPI server with all routes,
CORS, static files, and lifecycle management.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.api import topics, podcast, chat, stream
from backend.utils.logger import setup_logger
from contextlib import asynccontextmanager

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown tasks.
    """
    # Startup
    logger.info("🚀 Starting Endless AI Podcast backend")
    logger.info(f"OpenAI API configured: {'✓' if settings.openai_api_key else '✗'}")
    logger.info(f"Dust API configured: {'✓' if settings.dust_api_key else '✗'}")
    logger.info(f"Chat agents enabled: {settings.enable_chat_agents}")

    yield

    # Shutdown
    logger.info("👋 Shutting down Endless AI Podcast backend")


# Create FastAPI application
app = FastAPI(
    title="Endless AI Podcast API",
    description="Backend API for the Endless AI Podcast - a never-ending AI-generated podcast with community engagement",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (for audio)
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

# Include routers
app.include_router(topics.router)
app.include_router(podcast.router)
app.include_router(chat.router)
app.include_router(stream.router)


@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "Endless AI Podcast API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "topics": "/api/topics",
            "podcast": "/api/podcast/status",
            "chat": "/api/chat/messages",
            "stream": "/api/stream"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "supervisor_model": settings.supervisor_model,
        "content_model": settings.content_model,
        "features": {
            "chat_agents": settings.enable_chat_agents,
            "dust_integration": settings.enable_dust,
            "transcription": settings.enable_transcription
        }
    }


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting server on {settings.backend_host}:{settings.backend_port}")

    uvicorn.run(
        "backend.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
