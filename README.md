# 🎙️ Endless AI Podcast

A live, never-ending AI podcast where two LLM hosts discuss topics voted on by the community. Features real-time transcription, emoji reactions, and AI-generated chat engagement.

**Built for Copenhagen AI Hack 2025**

## 🌟 Features

- **🤖 Multi-LLM Architecture**: Supervisor (GPT-4o) + Content Generator (GPT-4o-mini) + 3 Chat Agents
- **🗣️ Two AI Hosts**: Alex (optimistic) and Mira (skeptical) with distinct voices
- **🎵 Text-to-Speech**: OpenAI TTS with realistic voices
- **👍👎 Emoji Voting**: React with thumbs up/down to influence topic selection
- **💬 AI Community Chat**: 3 AI personas simulate engaging community discussion
- **📝 Real-time Transcription**: Live text display of dialogue
- **⚡ Server-Sent Events**: Real-time updates without polling
- **🎯 Smart Topic Selection**: Weighted scoring based on votes and reactions

## 🏗️ Architecture

```
Supervisor (GPT-4o)
    ↓ Decides topics
Content Generator (GPT-4o-mini)
    ↓ Writes dialogue
OpenAI TTS
    ↓ Generates speech
Chat Agents (3x GPT-4o-mini)
    ↓ Community engagement
```

## 🛠️ Technology Stack

**Backend:**
- Python 3.11+
- FastAPI (async web framework)
- OpenAI API (GPT-4o, GPT-4o-mini, TTS)
- Dust API (orchestration)
- SSE-Starlette (real-time streaming)

**Frontend:**
- React + Vite (Lovable-generated)
- Tailwind CSS
- shadcn/ui components

## 📦 Setup Instructions

### 1. Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- OpenAI API key
- Dust API credentials (optional)

### 2. Clone Repository

```bash
cd Unlimited_Podcast
```

### 3. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

The `.env` file is already configured with your API keys. Verify it contains:

```env
OPENAI_API_KEY=sk-proj-...
DUST_API_KEY=sk-...
DUST_WORKSPACE_ID=FFvU3FTDcc
```

### 6. Run the Backend

```bash
# From project root
python -m backend.main

# Or using uvicorn directly
uvicorn backend.main:app --reload --port 8000
```

The backend will start on `http://localhost:8000`

### 7. Verify Installation

Open your browser and visit:
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

You should see the interactive API documentation.

## 🚀 Quick Start

### Test the API

1. **Create some topics:**
```bash
curl -X POST "http://localhost:8000/api/topic" \
  -H "Content-Type: application/json" \
  -d '{"text": "AI in Healthcare", "nickname": "TechFan123"}'

curl -X POST "http://localhost:8000/api/topic" \
  -H "Content-Type: application/json" \
  -d '{"text": "Future of Work", "nickname": "Futurist"}'
```

2. **Vote on topics:**
```bash
# Get topic ID from /api/topics, then:
curl -X POST "http://localhost:8000/api/vote" \
  -H "Content-Type: application/json" \
  -d '{"id": "TOPIC_ID_HERE", "delta": 1}'
```

3. **Start the podcast:**
```bash
curl -X POST "http://localhost:8000/api/podcast/start"
```

4. **Watch the magic happen!**
- The supervisor will select a topic
- Content generator creates dialogue
- TTS generates audio
- Chat agents start commenting
- Check `http://localhost:8000/static/audio/` for generated audio files

## 📡 API Endpoints

### Topics
- `POST /api/topic` - Create new topic
- `POST /api/vote` - Vote on topic (+1 or -1)
- `POST /api/react` - React with emoji (👍 or 👎)
- `GET /api/topics` - Get all topics sorted by score

### Podcast Control
- `POST /api/podcast/start` - Start podcast
- `POST /api/podcast/stop` - Stop podcast
- `GET /api/podcast/status` - Get current status
- `GET /api/podcast/transcript` - Get recent transcript

### Chat
- `POST /api/chat/message` - Send chat message
- `GET /api/chat/messages` - Get recent messages

### Streaming
- `GET /api/stream` - SSE stream for real-time updates

## 🎯 How It Works

### 20-Second Turn Cycle

Every 20 seconds:

1. **Supervisor Decides** (GPT-4o)
   - Analyzes votes and reactions
   - Decides: continue topic or switch?
   - Selects next topic if switching

2. **Content Generator Creates** (GPT-4o-mini)
   - Writes dialogue for both Alex and Mira
   - Maintains conversation flow
   - Creates distinct perspectives

3. **TTS Generates Audio** (OpenAI TTS)
   - Alex → "alloy" voice
   - Mira → "onyx" voice
   - Parallel generation for speed

4. **SSE Broadcasts** (Real-time)
   - NOW_PLAYING event
   - TRANSCRIPT_UPDATE event
   - Audio URLs sent to frontend

5. **Chat Agents React** (3x GPT-4o-mini)
   - Enthusiast: positive comments
   - Skeptic: critical questions
   - Curious: clarifying questions

### Weighted Scoring Algorithm

```python
score = (votes × 1) + (👍 × 5) + (👎 × -3)

# If current topic has ≥70% positive reactions:
#   → Continue current topic
# Else:
#   → Switch to highest-scored topic
```

## 🔧 Configuration

Edit `.env` to customize:

```env
# Duration of each turn (seconds)
PODCAST_TURN_DURATION=20

# Chat agent frequency (seconds)
CHAT_AGENT_INTERVAL=15

# Number of AI chat agents
CHAT_AGENT_COUNT=3

# Reaction weights
THUMBS_UP_WEIGHT=5
THUMBS_DOWN_WEIGHT=-3

# Topic continuation threshold (0.7 = 70%)
TOPIC_CONTINUATION_THRESHOLD=0.7
```

## 📁 Project Structure

```
Unlimited_Podcast/
├── backend/
│   ├── models/          # Pydantic models
│   ├── services/        # AI services (Supervisor, Content Gen, TTS, Chat)
│   ├── core/            # State management, scheduler
│   ├── api/             # FastAPI routes
│   ├── utils/           # Logger, helpers
│   ├── static/
│   │   └── audio/       # Generated podcast audio
│   ├── config.py        # Configuration from .env
│   └── main.py          # FastAPI application
├── .env                 # Environment variables (gitignored)
├── .env.example         # Template for .env
├── .gitignore
├── requirements.txt
└── README.md
```

## 🐛 Troubleshooting

### Import Errors

If you get `ModuleNotFoundError`, run from project root:
```bash
# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or use -m flag
python -m backend.main
```

### OpenAI API Errors

Check your API key:
```bash
# Test OpenAI connection
python -c "from openai import OpenAI; client = OpenAI(); print('✓ OpenAI connected')"
```

### Audio Files Not Generated

- Check `backend/static/audio/` directory exists
- Verify write permissions
- Check logs for TTS errors

### No Topics Available

The podcast needs at least one topic to start:
```bash
curl -X POST "http://localhost:8000/api/topic" \
  -H "Content-Type: application/json" \
  -d '{"text": "Getting Started with AI", "nickname": "Admin"}'
```

## 📊 Monitoring

### View Logs

The application logs to stdout. Key events:
- `Starting turn X` - New podcast turn
- `Topic selected` - Supervisor decision
- `Dialogue generated` - Content ready
- `Audio generated` - TTS complete
- `Chat agent comment` - AI community engagement

### Check Status

```bash
curl http://localhost:8000/api/podcast/status
```

### View Transcript

```bash
curl http://localhost:8000/api/podcast/transcript
```

## 🎨 Partner Technologies

This project uses 3 required partner tools:

1. **OpenAI** - GPT-4o (Supervisor), GPT-4o-mini (Content + Chat), TTS
2. **Dust** - Multi-agent orchestration (optional, can fallback to pure OpenAI)
3. **Lovable** - Frontend UI generation (React + Vite)

## 💰 Cost Estimates

Per 20-second turn:
- Supervisor (GPT-4o): ~$0.01
- Content Generator (GPT-4o-mini): ~$0.001
- Chat Agents (3x): ~$0.003
- TTS (2 voices): ~$0.03

**Total: ~$0.04 per turn**

1-hour demo: ~180 turns = **~$7.20**

## 🚀 Next Steps

### Frontend Setup (Coming Next)

1. Generate UI with Lovable
2. Export code
3. Connect to FastAPI backend
4. Add SSE client
5. Build audio player
6. Implement chat interface

### Enhancements

- [ ] Add Dust orchestration
- [ ] Transition sound effects
- [ ] Waveform visualization
- [ ] Topic history view
- [ ] User authentication
- [ ] Persistent storage

## 📝 License

MIT License - Built for Copenhagen AI Hack 2025

## 🤝 Contributing

This is a hackathon project. Feel free to fork and build upon it!

## 📧 Support

For issues or questions, check the API docs at `/docs` or review the logs.

---

**Built with ❤️ using OpenAI, Dust, and Lovable**
