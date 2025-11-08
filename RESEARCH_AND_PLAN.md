# Endless AI Podcast - Research & Implementation Plan (Python Edition)

## Executive Summary

**Project:** Endless AI Podcast - A live, never-ending AI podcast with two LLM hosts
**Timeline:** Hackathon day (9:30 AM - 5:00 PM submission)
**Target:** 2-minute demo video + public GitHub repo
**Tech Stack:** Python (FastAPI) backend + React (Vite) frontend

## 1. Technology Research (UPDATED)

### Selected Partner Technologies (3/6 required)

#### ✅ OpenAI (REQUIRED - PRIMARY)
- **Purpose:** Text generation + Text-to-Speech (TTS)
- **Python Integration:**
  - Official `openai` Python SDK (v1.x)
  - Streaming TTS support via `with_streaming_response.create()`
  - Can stream audio chunks directly to frontend
- **Capabilities:**
  - 6 neural voices: Alloy, Echo, Fable, Onyx, Nova, Shimmer
  - GPT-4o / GPT-4o-mini for dialogue generation
  - TTS models: `tts-1` (fast) or `tts-1-hd` (high quality)
  - Output formats: MP3, WAV, AAC
- **Usage in project:**
  - Generate dialogue for Alex & Mira personas
  - Convert text to speech with different voices
  - **Voices:** `alloy` (Alex - optimistic), `onyx` (Mira - skeptical)
- **Python Example:**
```python
from openai import OpenAI
client = OpenAI()

# Streaming TTS
with client.audio.speech.with_streaming_response.create(
    model="tts-1",
    voice="alloy",
    input="Hello! Welcome to Endless AI Podcast."
) as response:
    response.stream_to_file("output.mp3")
```

#### ✅ Dust (REQUIRED - SECONDARY)
- **Purpose:** Multi-agent orchestration
- **Python Integration:**
  - **No official Python SDK** (JavaScript only)
  - Use **REST API** directly via `requests` or `httpx`
  - OpenAPI definition available for reference
  - Authentication: Bearer token in headers
- **API Structure:**
```python
import requests

headers = {
    "Authorization": f"Bearer {DUST_API_KEY}",
    "Content-Type": "application/json"
}

# Trigger agent conversation
response = requests.post(
    f"https://dust.tt/api/v1/w/{WORKSPACE_ID}/agents/{AGENT_ID}/conversations",
    headers=headers,
    json={
        "message": {
            "role": "user",
            "content": f"Topic: {topic}. Speaker: {speaker}. Previous: {summary}"
        }
    }
)
```
- **Capabilities:**
  - Multi-agent workflows with Temporal orchestration
  - Supports GPT-4o, Claude 3, Gemini, Mistral
  - Context-aware conversations
- **Usage in project:**
  - Create two Dust agents: Alex (optimistic) and Mira (skeptical)
  - Orchestrate turn-taking with conversation context
  - Input: topic + last summary + speaker persona
  - Output: generated dialogue text + summary

#### ✅ Lovable (REQUIRED - TERTIARY)
- **Purpose:** Frontend UI generation
- **Integration Strategy (SIMPLIFIED):**
  - **Generate React + Vite app** in Lovable (native support)
  - **Export code** via GitHub sync → Download ZIP
  - **Customize** exported code in VS Code
  - **No conversion needed** - keep React + Vite!
- **Why React + Vite (not Next.js):**
  - ✅ Native Lovable output format
  - ✅ Faster development (no conversion overhead)
  - ✅ Simpler architecture for hackathon
  - ✅ Still meets requirement: "use Lovable for UI"
  - ✅ Vite has excellent dev experience
- **Lovable Workflow:**
  1. Describe UI: "Create a podcast interface with topic input, voting buttons, now playing card, audio player"
  2. Generate → Export via GitHub
  3. Download ZIP → Customize in VS Code
  4. Connect to FastAPI backend via fetch/axios
- **Stack:**
  - React 18+
  - Vite 5+
  - Tailwind CSS
  - shadcn/ui components
  - Supabase (optional, can remove if not needed)

### Optional Technologies (Not Using)

#### Weaviate
- Could add semantic topic search/deduplication
- **Decision:** Skip for MVP (adds complexity)

#### ACI.dev / Lightpanda
- **Decision:** Not relevant for this project

## 2. Technical Architecture (PYTHON)

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│              Frontend (React + Vite - Lovable)               │
│  - Topic input & voting UI (Lovable-generated)               │
│  - Now playing display (speaker, topic, countdown)           │
│  - Audio player (auto-queue segments)                        │
│  - EventSource SSE client (real-time updates)                │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP + SSE
┌────────────────────────┴────────────────────────────────────┐
│               Backend (Python + FastAPI)                     │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ API Routes  │  │  Scheduler   │  │ SSE Manager  │       │
│  │  (FastAPI)  │  │  (asyncio)   │  │(sse-starlette)│      │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ State Mgmt  │  │ Dust Client  │  │ OpenAI Client│       │
│  │ (in-memory) │  │(REST/httpx)  │  │(Python SDK)  │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                         │              │
                         ▼              ▼
                   ┌──────────┐   ┌──────────┐
                   │   Dust   │   │  OpenAI  │
                   │   API    │   │   API    │
                   └──────────┘   └──────────┘
```

### Data Flow (20-second Turn Cycle)

```
1. User submits topic → FastAPI endpoint → In-memory state (list)
2. Users vote → FastAPI endpoint → Update vote counts
3. Every 20 seconds (asyncio loop):
   ┌─────────────────────────────────────────────┐
   │ Scheduler (async background task)           │
   │ 1. Select top-voted topic                   │
   │ 2. Toggle speaker (Alex ↔ Mira)            │
   │ 3. Call Dust API (httpx):                   │
   │    POST /conversations                      │
   │    Input: {topic, lastSummary, speaker}     │
   │    Output: {dialogueText, shortSummary}     │
   │ 4. Call OpenAI TTS (streaming):             │
   │    client.audio.speech.create()             │
   │    Save audio file to /static/audio/        │
   │ 5. Update nowPlaying state                  │
   │ 6. Broadcast SSE events:                    │
   │    - TOPICS_UPDATED                         │
   │    - NOW_CHANGED                            │
   │    - AUDIO_SEGMENT_READY {url}              │
   └─────────────────────────────────────────────┘
4. Frontend receives SSE → Updates UI → Plays audio via <audio> element
```

## 3. Implementation Plan (PYTHON)

### Phase 1: Setup (30 minutes)
- [x] Research technologies (Python + FastAPI + OpenAI + Dust + Lovable)
- [ ] Create project structure (backend/ + frontend/)
- [ ] Initialize Python virtual environment
- [ ] Install dependencies (fastapi, uvicorn, openai, httpx, sse-starlette, python-dotenv)
- [ ] Set up .env.example
- [ ] Initialize Lovable project for frontend

### Phase 2: Backend Core (1.5 hours)
- [ ] FastAPI server setup with CORS
- [ ] In-memory state management (`AppState` class)
  - `topics: List[Topic]` (id, text, votes)
  - `now_playing: Optional[NowPlaying]`
  - `podcast_running: bool`
  - `last_summary: str`
- [ ] Pydantic models (Topic, NowPlaying, Vote, etc.)
- [ ] Basic API routes (POST /topic, POST /vote, GET /topics, GET /now)
- [ ] SSE endpoint (GET /stream) with sse-starlette

### Phase 3: OpenAI Integration (1.5 hours)
- [ ] OpenAI client setup (`openai` Python SDK)
- [ ] Dialogue generation function:
  - `generate_dialogue(topic, speaker, last_summary) -> str`
  - Use GPT-4o-mini with persona system prompts
- [ ] TTS generation function:
  - `generate_audio(text, voice) -> str` (returns file path)
  - Stream to file using `with_streaming_response.create()`
  - Save to `/static/audio/{timestamp}.mp3`
- [ ] Error handling & retries

### Phase 4: Dust API Integration (1 hour)
- [ ] Dust REST client (`httpx.AsyncClient`)
- [ ] Authentication setup (Bearer token)
- [ ] Agent creation (via Dust UI or API):
  - Create "Alex" agent (optimistic system prompt)
  - Create "Mira" agent (skeptical system prompt)
- [ ] Turn orchestration function:
  - `dust_generate_turn(topic, speaker, last_summary) -> dict`
  - Call appropriate agent based on speaker
  - Parse response for dialogue text
- [ ] Fallback to OpenAI if Dust fails

### Phase 5: Scheduler Logic (1 hour)
- [ ] Background task with `asyncio.create_task()`
- [ ] 20-second interval loop (`asyncio.sleep(20)`)
- [ ] Topic selection algorithm (max votes, tie-break by timestamp)
- [ ] Speaker alternation (toggle between Alex/Mira)
- [ ] Async audio generation pipeline
- [ ] State updates + SSE broadcast
- [ ] Start/stop endpoints (POST /podcast/start, POST /podcast/stop)

### Phase 6: Frontend with Lovable (2 hours)
- [ ] Generate initial UI in Lovable:
  - Prompt: "Create podcast UI with topic input, voting, now playing card, audio player, real-time updates"
- [ ] Export via GitHub → Download
- [ ] Customize in VS Code:
  - Remove Supabase if not needed
  - Add EventSource for SSE connection
  - Connect API endpoints (fetch to FastAPI)
  - Implement audio auto-play logic
  - Add countdown timer (20s)
  - Speaker avatars/icons
- [ ] Tailwind styling refinements

### Phase 7: Integration & Testing (1 hour)
- [ ] End-to-end testing (topic → vote → podcast → audio)
- [ ] Error handling improvements
- [ ] CORS configuration
- [ ] Audio file cleanup (delete old segments)
- [ ] UI/UX polish

### Phase 8: Demo Preparation (30 minutes)
- [ ] README with setup instructions
- [ ] Record 2-minute Loom video
- [ ] Push to public GitHub repo
- [ ] Prepare presentation talking points

## 4. Technical Specifications (PYTHON)

### Project Structure

```
Unlimited_Podcast/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── models.py            # Pydantic models
│   ├── state.py             # In-memory state management
│   ├── scheduler.py         # 20s podcast loop
│   ├── dust_client.py       # Dust REST API client
│   ├── openai_client.py     # OpenAI SDK wrapper
│   ├── sse.py               # SSE event broadcasting
│   ├── static/
│   │   └── audio/           # Generated audio files
│   ├── requirements.txt
│   └── .env
├── frontend/                # Lovable-generated React + Vite
│   ├── src/
│   │   ├── components/
│   │   ├── App.tsx
│   │   └── api.ts          # Backend API client
│   ├── package.json
│   └── vite.config.ts
├── .env.example
└── README.md
```

### API Endpoints (FastAPI)

```python
# Topics
POST   /api/topic           { "text": str }
POST   /api/vote            { "id": str, "delta": int }  # delta = 1 or -1
GET    /api/topics          → List[Topic]

# Podcast control
GET    /api/now             → NowPlaying | None
POST   /api/podcast/start   → {"status": "started"}
POST   /api/podcast/stop    → {"status": "stopped"}

# Real-time updates
GET    /api/stream          → SSE stream

# Static files
GET    /static/audio/{filename}.mp3  → audio file
```

### Pydantic Models

```python
from pydantic import BaseModel
from typing import Optional

class Topic(BaseModel):
    id: str
    text: str
    votes: int
    created_at: float

class NowPlaying(BaseModel):
    topic_id: str
    topic_text: str
    speaker: str  # "Alex" or "Mira"
    audio_url: str
    started_at: float
    ends_at: float

class VoteRequest(BaseModel):
    id: str
    delta: int  # 1 or -1

class TopicRequest(BaseModel):
    text: str
```

### Environment Variables

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Dust
DUST_API_KEY=...
DUST_WORKSPACE_ID=...
DUST_AGENT_ALEX_ID=...
DUST_AGENT_MIRA_ID=...

# Voices
VOICE_ALEX=alloy
VOICE_MIRA=onyx

# Server
PORT=8000
FRONTEND_URL=http://localhost:5173
```

### Persona Definitions (Python)

```python
PERSONAS = {
    "Alex": {
        "name": "Alex",
        "role": "Optimistic Visionary",
        "voice": "alloy",
        "system_prompt": """You are Alex, an enthusiastic and optimistic podcast host.
        You see potential and possibilities in every topic. Speak conversationally
        in 2-3 sentences (max 100 words). Be engaging and forward-thinking.""",
        "dust_agent_id": os.getenv("DUST_AGENT_ALEX_ID"),
    },
    "Mira": {
        "name": "Mira",
        "role": "Skeptical Pragmatist",
        "voice": "onyx",
        "system_prompt": """You are Mira, a thoughtful and pragmatic podcast host.
        You ask tough questions and consider practical implications. Speak
        conversationally in 2-3 sentences (max 100 words). Be analytical but friendly.""",
        "dust_agent_id": os.getenv("DUST_AGENT_MIRA_ID"),
    }
}
```

### SSE Event Types

```python
# Events sent from backend to frontend
{
    "event": "TOPICS_UPDATED",
    "data": {
        "topics": [...]
    }
}

{
    "event": "NOW_CHANGED",
    "data": {
        "topic_id": "...",
        "topic_text": "...",
        "speaker": "Alex",
        "audio_url": "/static/audio/123.mp3",
        "started_at": 1234567890.0,
        "ends_at": 1234567910.0
    }
}

{
    "event": "AUDIO_READY",
    "data": {
        "url": "/static/audio/123.mp3"
    }
}
```

## 5. Python Dependencies

```txt
# requirements.txt
fastapi==0.115.0
uvicorn[standard]==0.32.0
python-dotenv==1.0.1
pydantic==2.10.0
openai==1.58.1
httpx==0.28.1
sse-starlette==2.2.1
python-multipart==0.0.20
```

## 6. Risks & Mitigation (UPDATED)

### Risk 1: Dust API complexity (No Python SDK)
- **Mitigation:** Use `httpx` for REST API calls, reference OpenAPI docs
- **Backup:** Skip Dust entirely, use OpenAI directly with persona prompts
- **Test plan:** Implement OpenAI fallback first, add Dust as enhancement

### Risk 2: Audio streaming & storage
- **Mitigation:** Save audio files to `/static/audio/`, serve via FastAPI StaticFiles
- **Cleanup:** Delete files older than 1 hour in background task
- **Backup:** Use base64-encoded audio in SSE (slower but simpler)

### Risk 3: Lovable → Backend integration
- **Mitigation:** Use standard REST API + SSE (framework-agnostic)
- **Testing:** Test SSE with curl first, then integrate frontend
- **Backup:** Polling instead of SSE if EventSource has issues

### Risk 4: Time constraints
- **Priority order:**
  1. ✅ OpenAI TTS + basic dialogue (essential)
  2. ✅ Topic voting + selection (core feature)
  3. ✅ 20s scheduler loop (core feature)
  4. ✅ Lovable UI (requirement)
  5. ⚠️ Dust orchestration (nice-to-have, can fallback to OpenAI)
  6. ⚠️ SSE (can use polling as backup)

## 7. Success Criteria

### Minimum Viable Demo (Must Have)
- ✅ Users can submit topics (POST /api/topic)
- ✅ Users can vote on topics (POST /api/vote)
- ✅ Every 20 seconds, top topic is selected
- ✅ Two AI personas alternate speaking (Alex ↔ Mira)
- ✅ Audio plays automatically in browser
- ✅ UI updates in real-time (SSE or polling)
- ✅ Uses OpenAI + Dust + Lovable (3 partner tools)

### Bonus Features (Nice to Have)
- Advanced Dust multi-agent conversation (context-aware)
- Audio waveform visualization
- Topic history with replay
- Speaker avatar animations
- Vote count live updates
- Mobile responsive design
- Audio transcription display

## 8. Hackathon Compliance Checklist

- ✅ Team size: Max 5 people
- ✅ Use minimum 3 partner technologies:
  1. **OpenAI** (TTS + dialogue generation)
  2. **Dust** (multi-agent orchestration via REST API)
  3. **Lovable** (React + Vite UI generation)
- ✅ Created newly at hackathon (boilerplate allowed)
- [ ] 2-minute video demo (Loom)
- [ ] Public GitHub repository
- [ ] Comprehensive README
- [ ] Submit by 17:00

## 9. Demo Script Outline (2 minutes)

```
0:00-0:20  Introduction
           - "Endless AI Podcast - live, never-ending AI conversation"
           - "Two personas: Alex (optimistic) & Mira (skeptical)"
           - "Users vote on topics, AI responds in real-time"

0:20-0:45  User Interaction Demo
           - Submit 3 topics: "AI in Healthcare", "Future of Work", "Climate Tech"
           - Show voting in action (upvote/downvote)
           - Highlight real-time updates (SSE)

0:45-1:20  Podcast in Action
           - Click "Start Podcast"
           - Show 20s countdown timer
           - Alex speaks on top topic (optimistic take)
           - Auto-play audio
           - Mira responds after 20s (skeptical perspective)
           - Show speaker alternation

1:20-1:45  Technical Highlights
           - "Python FastAPI backend with OpenAI + Dust"
           - "Lovable-generated React UI"
           - "Real-time SSE updates, no database"
           - Show code snippet (scheduler.py)

1:45-2:00  Conclusion
           - "Built in one day at Copenhagen AI Hack"
           - "Uses OpenAI, Dust, and Lovable"
           - GitHub link + live demo
```

## 10. Technology Stack Summary

**Frontend:**
- ⚡ React 18+ (generated by Lovable)
- ⚡ Vite 5+ (fast dev server)
- 🎨 Tailwind CSS
- 🎨 shadcn/ui components
- 🔄 EventSource (SSE client)
- 📦 axios or fetch for API calls

**Backend:**
- 🐍 Python 3.11+
- ⚡ FastAPI (async web framework)
- 🔊 OpenAI Python SDK (TTS + chat)
- 🤖 Dust REST API (httpx)
- 📡 sse-starlette (SSE streaming)
- ⏱️ asyncio (scheduler loop)

**Infrastructure:**
- 📂 Simple folder structure (backend/ + frontend/)
- 💾 No database (in-memory only)
- 📡 SSE for real-time updates
- 🔧 Local development only

**APIs Used:**
- OpenAI API (text generation + TTS)
- Dust API (multi-agent orchestration)
- No third-party databases

---

## 11. Implementation Strategy

### Phase A: Backend First (Priority)
Why: Backend is the critical path. Frontend is simpler to build once backend works.

1. **Hour 1:** FastAPI skeleton + OpenAI integration
2. **Hour 2:** Scheduler loop + audio generation
3. **Hour 3:** Dust integration + SSE streaming

### Phase B: Frontend with Lovable
Why: Lovable generates 80% of UI, we customize the remaining 20%.

1. **30 min:** Generate UI in Lovable, export
2. **90 min:** Customize (add SSE, connect API, audio player)

### Phase C: Integration & Demo
1. **Hour 1:** Test end-to-end, fix bugs
2. **30 min:** Record demo, push to GitHub

---

## 12. Next Steps

### Immediate Actions:
1. ✅ Set up Python virtual environment
2. ✅ Install FastAPI + dependencies
3. ✅ Create basic FastAPI server with CORS
4. ✅ Test OpenAI TTS (generate sample audio)
5. ✅ Implement in-memory state management

### Then:
6. Build scheduler loop
7. Integrate Dust API
8. Generate Lovable UI
9. Connect frontend to backend
10. Test & demo

---

**Status:** Research complete ✅ | Python architecture designed ✅ | Ready to code backend 🚀
