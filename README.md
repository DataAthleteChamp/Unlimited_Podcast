# 🎙️ Endless AI Podcast

A live, never-ending AI podcast where two LLM hosts (Alex and Mira) discuss community-voted topics in a queue-based system. Features real-time audio generation, visual waveforms, AI-powered chat, and a full-stack React interface.

**Built for Copenhagen AI Hack 2025**

## 🌟 Features

### Core Podcast Features
- **🎯 Queue-Based Topic System**: FIFO queue with position tracking and estimated wait times
- **🤖 Multi-Agent AI Architecture**: Supervisor (GPT-4o) + Content Generator (GPT-4o-mini) + 3 Chat Agents
- **🗣️ Two AI Hosts**: Alex (optimistic, "alloy" voice) and Mira (skeptical, "onyx" voice)
- **🎵 Real Audio Generation**: OpenAI TTS-1 with parallel voice synthesis
- **📊 40-Bar Audio Visualizer**: Animated waveform with speaker-specific color gradients
- **📝 Live Transcription**: Real-time dialogue display with color-coded speakers

### Community Engagement
- **💬 AI-Powered Topic Suggestions**: GPT-4o-mini analyzes chat to generate relevant topics
- **👍👎 Voting & Reactions**: Vote on topics and add emoji reactions
- **🎭 AI Community Simulation**: 3 distinct personas (Enthusiast, Skeptic, Curious)
- **⚡ Server-Sent Events**: Real-time updates with no polling lag
- **🎮 Interactive Controls**: Start/stop podcast, manage queue, track status

## 💡 Key Innovations

### 1. Queue-Based Architecture
Unlike traditional chatbots that maintain conversation context, this system uses a **FIFO queue** for predictable topic progression. Each topic gets a fresh conversation with no context carryover, ensuring:
- **Reliability**: No context drift or degradation over time
- **Predictability**: Users know exactly when their topic will play
- **Freshness**: Every conversation is independent and focused

### 2. Multi-Agent Orchestration
The system employs **specialized AI agents** for different tasks:
- **Supervisor**: Strategic planning (when to switch topics)
- **Content Generator**: Creative dialogue writing
- **Chat Agents**: Community simulation with distinct personalities
- **Optional Dust Integration**: Enhanced orchestration with memory management

### 3. Real Audio Generation
This isn't just text - it's a **real podcast** with:
- OpenAI TTS-1 generating actual MP3 files
- Parallel voice synthesis for speed (Alex + Mira simultaneously)
- Distinct voices creating natural conversation dynamics
- Visual feedback via animated waveforms

### 4. Full-Stack Real-Time System
Built with modern async patterns:
- **Backend**: FastAPI with async/await for concurrent operations
- **Frontend**: React + TypeScript with React Query for data management
- **Communication**: Server-Sent Events (SSE) for sub-second latency
- **State Management**: Centralized singleton with thread-safe operations

### 5. AI-Powered Community
Instead of requiring real users, the system **simulates engagement** with AI personas:
- Reduces cold-start problem
- Creates lively atmosphere even with few users
- Each persona has distinct personality and commentary style
- Generates realistic, contextual comments (10-20 words)

## 🏗️ Architecture

### Queue-Based Flow
```
User Votes → Topic Queue (FIFO)
    ↓
Scheduler pulls next topic
    ↓
Content Generator (GPT-4o-mini) - Fresh dialogue
    ↓
OpenAI TTS (parallel) - Alex (alloy) + Mira (onyx)
    ↓
SSE Broadcast - NOW_PLAYING event
    ↓
Chat Agents (3x GPT-4o-mini) - Community reactions
    ↓
Next topic (30s later)
```

### Full-Stack Architecture
```
Frontend (React + Vite)
    ├── RealAudioPlayer (visualizer + playback)
    ├── QueueView (FIFO queue display)
    ├── ChatSidebar (AI topic generation)
    ├── PodcastControls (start/stop)
    └── TranscriptView (live dialogue)
         ↕ SSE + REST API
Backend (FastAPI)
    ├── State Manager (in-memory)
    ├── Scheduler (20s turn loop)
    ├── Content Generator (GPT-4o-mini)
    ├── TTS Service (OpenAI)
    └── Chat Agents (3x personas)
```

## 🛠️ Technology Stack

**Backend:**
- Python 3.11+
- FastAPI 0.115.0+ (async web framework)
- Uvicorn (ASGI server with hot reload)
- OpenAI API (GPT-4o, GPT-4o-mini, TTS-1)
- Dust API (optional orchestration)
- SSE-Starlette 2.0.0+ (real-time streaming)
- Pydantic 2.0+ (data validation)
- HTTPX (async HTTP client)

**Frontend:**
- React 18.3.1 + TypeScript 5.8.3
- Vite 5.4.19 (build tool + dev server)
- shadcn/ui (40+ components via Radix UI)
- Tailwind CSS 3.4.17 (utility-first styling)
- React Query 5.83.0 (data fetching)
- React Router DOM 6.30.1 (routing)
- React Hook Form 7.61.1 + Zod 3.25.76 (forms)
- Recharts 2.15.4 (charts)
- Lucide React 0.462.0 (icons)
- Sonner 1.7.4 (toast notifications)

## 📦 Setup Instructions

### 1. Prerequisites

- Python 3.11 or higher
- Node.js 18+ and npm
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

### 7. Verify Backend

Open your browser and visit:
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

You should see the interactive API documentation.

### 8. Set Up Frontend

Open a **new terminal** (keep backend running):

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will start on `http://localhost:8081`

### 9. Access the Application

Open your browser and visit `http://localhost:8081` to see the full interface with:
- Real-time audio player with visualizer
- Topic voting and queue management
- Chat interface for topic suggestions
- Live transcript display
- Podcast controls

## 🚀 Quick Start

### Using the Web Interface (Recommended)

1. Open `http://localhost:8081` in your browser
2. Enter a username when prompted
3. Type messages in the chat to generate topic suggestions
4. Vote on topics to add them to the queue
5. Click "Start Podcast" to begin
6. Watch the queue progress and listen to the podcast!

### Using the API (Advanced)

1. **Create and queue topics:**
```bash
# Create a topic
curl -X POST "http://localhost:8000/api/topic" \
  -H "Content-Type: application/json" \
  -d '{"text": "AI in Healthcare", "nickname": "TechFan123"}'

# Get topic ID from response, then add to queue
curl -X POST "http://localhost:8000/api/podcast/queue/add/TOPIC_ID_HERE"
```

2. **Generate AI topic suggestions from chat:**
```bash
curl -X POST "http://localhost:8000/api/topics/suggestions" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"text": "I love discussing AI and robotics!", "nickname": "User1"}]}'
```

3. **Start the podcast:**
```bash
curl -X POST "http://localhost:8000/api/podcast/start"
```

4. **Watch the queue progress:**
```bash
# Check queue status
curl http://localhost:8000/api/podcast/queue

# Monitor current playing
curl http://localhost:8000/api/podcast/now
```

5. **Experience the podcast:**
- Topics process in FIFO order
- Fresh dialogue generated for each topic
- TTS creates MP3 files (Alex: alloy, Mira: onyx)
- Chat agents react to the conversation
- Check `http://localhost:8000/static/audio/` for audio files

## 📡 API Endpoints

### Topics
- `POST /api/topic` - Create new topic
- `POST /api/vote` - Vote on topic (+1 or -1)
- `POST /api/react` - React with emoji (👍 or 👎)
- `GET /api/topics` - Get all topics sorted by score
- `POST /api/topics/suggestions` - Generate AI topic suggestions from chat messages

### Podcast Control
- `POST /api/podcast/start` - Start podcast scheduler
- `POST /api/podcast/stop` - Stop podcast scheduler
- `GET /api/podcast/status` - Get current status (running, uptime, turn count)
- `GET /api/podcast/transcript` - Get recent transcript entries
- `GET /api/podcast/now` - Get currently playing audio information
- `GET /api/podcast/queue` - Get queue information (now playing + upcoming)
- `POST /api/podcast/queue/add/{topic_id}` - Add topic to podcast queue

### Chat
- `POST /api/chat/message` - Send chat message
- `GET /api/chat/messages` - Get recent messages

### Streaming
- `GET /api/stream` - SSE stream for real-time updates (NOW_PLAYING, TOPIC_CHANGED, QUEUE_UPDATED, CHAT_MESSAGE events)

### Static Files
- `GET /static/audio/{filename}` - Access generated MP3 audio files

## 🎨 User Experience

### Complete User Journey

1. **Open Application** (`http://localhost:8081`)
   - Welcome screen with project description
   - Navigate to Dashboard

2. **Enter the Community**
   - Username prompt on first visit
   - Join the live chat

3. **Generate Topics**
   - Type messages in chat (e.g., "I'm interested in AI safety and robotics")
   - Click "Generate Topics" button
   - AI analyzes chat messages and suggests 3 relevant topics
   - Topics appear as cards with vote buttons

4. **Vote & Queue**
   - Click vote button on topics you like
   - Topic gets added to the queue
   - See queue position and estimated wait time (e.g., "Position #3 - ~6 minutes")

5. **Start the Podcast**
   - Click "Start Podcast" button
   - Scheduler begins processing queue in FIFO order

6. **Experience the Live Podcast**
   - **Audio Player**: Auto-plays MP3 with visual 40-bar waveform
     - Yellow-orange gradient for Alex
     - Pink-purple gradient for Mira
   - **Transcript View**: Live dialogue updates with speaker colors
   - **Queue View**: Shows "Now Playing" + upcoming topics
   - **Status Panel**: Uptime, turn count, current topic
   - **Chat Sidebar**: AI personas comment on the discussion

7. **Continuous Loop**
   - Each topic plays for ~30 seconds
   - Fresh conversation per topic (no context carryover)
   - Queue automatically advances to next topic
   - AI chat agents engage throughout

## 🎯 How It Works

### Queue-Based System

The podcast operates on a **FIFO (First In, First Out) queue** for predictable, user-controlled topic progression:

1. **Users Chat & Vote**
   - Type messages in chat interface
   - AI analyzes messages → generates 3 topic suggestions
   - Vote on topics → gets added to queue
   - Each topic shows queue position & estimated wait time

2. **Podcast Loop** (~30 seconds per topic)

   **a) Topic Selection**
   - Scheduler pulls next topic from queue (FIFO)
   - Clears transcript for fresh conversation
   - Broadcasts `TOPIC_CHANGED` event via SSE

   **b) Content Generation** (GPT-4o-mini)
   - Creates fresh dialogue with no context carryover
   - Alex: Optimistic, forward-thinking perspective
   - Mira: Skeptical, pragmatic counterpoint
   - Returns JSON: `{alex, mira, summary}`

   **c) Audio Generation** (OpenAI TTS-1)
   - Parallel processing for speed:
     - Alex → "alloy" voice → alex.mp3
     - Mira → "onyx" voice → mira.mp3
   - Saves to `backend/static/audio/`

   **d) SSE Broadcast** (Real-time)
   - Sends `NOW_PLAYING` event with audio URLs
   - Frontend auto-loads and plays MP3
   - Updates transcript, visualizer, and queue view

   **e) Community Simulation** (3x GPT-4o-mini)
   - Runs asynchronously every 15 seconds
   - Three AI personas generate comments:
     - **Enthusiast**: Positive, supportive (10-20 words)
     - **Skeptic**: Critical, questioning (10-20 words)
     - **Curious**: Neutral, inquisitive (10-20 words)
   - Broadcasts `CHAT_MESSAGE` events

   **f) Loop Continues**
   - Marks topic as "used" (prevents repetition)
   - Waits 5 seconds
   - Pulls next topic from queue
   - Repeats indefinitely until stopped

### Weighted Voting System

Topics are prioritized for queue entry based on score:

```python
score = (votes × 1) + (👍 × 5) + (👎 × -3) + recency_bonus

# Recency bonus decays over 1 hour
# Higher score = more attractive for voting
```

Once in queue, topics are processed **strictly in order** (FIFO).

## 🔧 Configuration

Edit `.env` to customize behavior:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-...
SUPERVISOR_MODEL=gpt-4o
CONTENT_MODEL=gpt-4o-mini
VOICE_ALEX=alloy
VOICE_MIRA=onyx
TTS_MODEL=tts-1

# Dust Configuration (Optional)
DUST_API_KEY=sk-...
DUST_WORKSPACE_ID=your_workspace_id
DUST_AGENT_SUPERVISOR_ID=agent_xxxxx
DUST_AGENT_CONTENT_ID=agent_yyyyy

# Server Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Feature Flags
ENABLE_CHAT_AGENTS=true        # Enable AI community simulation
ENABLE_DUST=false              # Use Dust API (fallback to OpenAI)
CHAT_AGENT_COUNT=3             # Number of AI personas

# Podcast Configuration
PODCAST_TURN_DURATION=20       # Duration of each turn (seconds)
CHAT_AGENT_INTERVAL=15         # Chat agent comment frequency (seconds)

# Voting Configuration
VOTE_WEIGHT=1                  # Weight for each vote
THUMBS_UP_WEIGHT=5            # Weight for 👍 reaction
THUMBS_DOWN_WEIGHT=-3         # Weight for 👎 reaction
TOPIC_CONTINUATION_THRESHOLD=0.7  # (Legacy - not used in queue mode)
```

## 📁 Project Structure

```
Unlimited_Podcast/
├── backend/
│   ├── api/
│   │   ├── topics.py         # Topic management endpoints
│   │   ├── podcast.py        # Podcast control & queue endpoints
│   │   └── chat.py           # Chat message endpoints
│   ├── core/
│   │   ├── state.py          # Application state manager (singleton)
│   │   └── scheduler.py      # Podcast scheduler (queue-based loop)
│   ├── models/
│   │   ├── topic.py          # Topic, Vote, Reaction models
│   │   ├── podcast.py        # Dialogue, Transcript models
│   │   └── chat.py           # ChatMessage model
│   ├── services/
│   │   ├── supervisor.py     # Topic selection (GPT-4o)
│   │   ├── content_generator.py  # Dialogue generation (GPT-4o-mini)
│   │   ├── tts_service.py    # Text-to-speech (OpenAI TTS)
│   │   ├── chat_agents.py    # AI community simulation (3x agents)
│   │   └── dust_client.py    # Dust API integration (optional)
│   ├── utils/
│   │   └── logger.py         # JSON logging configuration
│   ├── static/
│   │   └── audio/            # Generated MP3 files (alex.mp3, mira.mp3)
│   ├── config.py             # Environment configuration (Pydantic)
│   └── main.py               # FastAPI app + SSE endpoint
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── RealAudioPlayer.tsx   # Audio player + 40-bar visualizer
│   │   │   ├── PodcastControls.tsx   # Start/Stop buttons
│   │   │   ├── PodcastStatus.tsx     # Status display (uptime, turns)
│   │   │   ├── QueueView.tsx         # Queue management UI
│   │   │   ├── ChatSidebar.tsx       # Chat interface
│   │   │   ├── TopicCard.tsx         # Topic voting card
│   │   │   ├── TranscriptView.tsx    # Live dialogue display
│   │   │   └── ui/                   # shadcn/ui components (40+)
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx         # Main application page
│   │   │   └── Index.tsx             # Landing page
│   │   ├── lib/
│   │   │   └── utils.ts              # Utility functions
│   │   ├── App.tsx                   # React Router setup
│   │   └── main.tsx                  # Entry point
│   ├── public/                       # Static assets
│   ├── package.json                  # Frontend dependencies
│   ├── vite.config.ts                # Vite build configuration
│   ├── tailwind.config.ts            # Tailwind CSS config
│   └── tsconfig.json                 # TypeScript configuration
├── .env                              # Environment variables (gitignored)
├── .env.example                      # Template for .env
├── .gitignore
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

## 🐛 Troubleshooting

### Backend Issues

**Import Errors**

If you get `ModuleNotFoundError`, run from project root:
```bash
# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or use -m flag
python -m backend.main
```

**OpenAI API Errors**

Check your API key:
```bash
# Test OpenAI connection
python -c "from openai import OpenAI; client = OpenAI(); print('✓ OpenAI connected')"
```

**Audio Files Not Generated**

- Check `backend/static/audio/` directory exists
- Verify write permissions
- Check logs for TTS errors
- Ensure OpenAI API key has TTS access

**Empty Queue**

The podcast needs topics in the queue to start:
1. Use the frontend to vote on topics
2. Or use the API to add topics to queue:
```bash
curl -X POST "http://localhost:8000/api/topic" \
  -H "Content-Type: application/json" \
  -d '{"text": "Getting Started with AI", "nickname": "Admin"}'
```

### Frontend Issues

**Port Already in Use**

If port 8081 is busy, edit `frontend/vite.config.ts`:
```typescript
server: {
  port: 3000  // Change to any available port
}
```

**CORS Errors**

Ensure backend `.env` has correct frontend URL:
```env
FRONTEND_URL=http://localhost:8081
CORS_ORIGINS=http://localhost:8081,http://127.0.0.1:8081
```

**Audio Not Playing**

- Check browser console for errors
- Ensure backend is serving audio files at `/static/audio/`
- Try manually accessing: `http://localhost:8000/static/audio/alex.mp3`
- Some browsers block autoplay - click the audio player manually

**SSE Connection Failed**

- Verify backend is running on port 8000
- Check browser network tab for `/api/stream` connection
- Ensure no proxy/firewall blocking SSE

**NPM Install Fails**

Try clearing cache and reinstalling:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
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

## 🚀 Future Enhancements

### Completed ✅
- ✅ Full-stack React frontend with TypeScript
- ✅ SSE client for real-time updates
- ✅ Audio player with auto-play
- ✅ 40-bar waveform visualizer with speaker colors
- ✅ Chat interface with AI topic generation
- ✅ Queue-based topic system
- ✅ Dust orchestration integration (optional)

### Potential Improvements
- [ ] Transition sound effects between topics
- [ ] Topic history view (archive of discussed topics)
- [ ] User authentication & profiles
- [ ] Persistent storage (database instead of in-memory)
- [ ] Analytics dashboard (voting patterns, popular topics)
- [ ] Multi-room support (different podcast channels)
- [ ] Export podcast episodes as downloadable files
- [ ] Mobile-responsive design improvements
- [ ] Dark mode theme toggle
- [ ] Custom voice selection (beyond alloy/onyx)

## 📝 License

MIT License - Built for Copenhagen AI Hack 2025

## 🤝 Contributing

This is a hackathon project. Feel free to fork and build upon it!

## 📧 Support

For issues or questions, check the API docs at `/docs` or review the logs.

---

**Built with ❤️ using OpenAI, Dust, and Lovable**
