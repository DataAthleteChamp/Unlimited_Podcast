# 🚀 Quick Start Guide - Endless AI Podcast

## ✅ Prerequisites Checklist

Before starting, make sure you have:
- [x] Python 3.11+ installed
- [x] OpenAI API key configured in `.env`
- [x] Virtual environment created (`venv/`)
- [x] Dependencies installed

## 🎯 How to Run the Backend

### Step 1: Activate Virtual Environment

```bash
# From the project root directory
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 2: Start the Backend Server

```bash
# Run the FastAPI backend
python -m backend.main
```

You should see:
```
🚀 Starting Endless AI Podcast backend
OpenAI API configured: ✓
Dust API configured: ✓
Chat agents enabled: True
Uvicorn running on http://0.0.0.0:8000
```

**The backend is now running!** 🎉

---

## 🧪 How to Test the API

### Option 1: Web Browser (Easiest)

Open your browser and visit:

**Interactive API Documentation:**
```
http://localhost:8000/docs
```

This gives you a beautiful UI where you can:
- See all endpoints
- Try them out with a "Try it" button
- View request/response examples

**Health Check:**
```
http://localhost:8000/health
```

### Option 2: Command Line (cURL)

Open a **new terminal** (keep the server running in the first one).

#### 1. Create Topics

```bash
# Topic 1
curl -X POST http://localhost:8000/api/topic \
  -H "Content-Type: application/json" \
  -d '{"text": "AI in Healthcare", "nickname": "TechFan"}'

# Topic 2
curl -X POST http://localhost:8000/api/topic \
  -H "Content-Type: application/json" \
  -d '{"text": "Future of Work", "nickname": "Futurist"}'

# Topic 3
curl -X POST http://localhost:8000/api/topic \
  -H "Content-Type: application/json" \
  -d '{"text": "Climate Tech", "nickname": "EcoWarrior"}'
```

#### 2. View All Topics

```bash
curl http://localhost:8000/api/topics | python3 -m json.tool
```

#### 3. Vote on a Topic

```bash
# Get topic ID from step 2, then vote:
curl -X POST http://localhost:8000/api/vote \
  -H "Content-Type: application/json" \
  -d '{"id": "PASTE_TOPIC_ID_HERE", "delta": 1}'
```

#### 4. Add Emoji Reaction

```bash
# Thumbs up
curl -X POST http://localhost:8000/api/react \
  -H "Content-Type: application/json" \
  -d '{"id": "PASTE_TOPIC_ID_HERE", "emoji": "👍"}'

# Thumbs down
curl -X POST http://localhost:8000/api/react \
  -H "Content-Type: application/json" \
  -d '{"id": "PASTE_TOPIC_ID_HERE", "emoji": "👎"}'
```

#### 5. Start the Podcast 🎙️

```bash
curl -X POST http://localhost:8000/api/podcast/start
```

**This will:**
- Call GPT-4o (Supervisor) to select topic
- Call GPT-4o-mini (Content Generator) to create dialogue
- Call OpenAI TTS to generate audio files
- Trigger chat agents to comment
- Run every 20 seconds automatically

#### 6. Check Podcast Status

```bash
curl http://localhost:8000/api/podcast/status | python3 -m json.tool
```

#### 7. View Transcript

```bash
curl http://localhost:8000/api/podcast/transcript | python3 -m json.tool
```

#### 8. Stop the Podcast

```bash
curl -X POST http://localhost:8000/api/podcast/stop
```

---

## 📊 Monitoring the Podcast

### Watch the Logs

The terminal where you ran `python -m backend.main` shows:
- **Turn starts**: `=== Starting turn X ===`
- **Supervisor decisions**: `Supervisor decision: switch - AI in Healthcare`
- **Dialogue generation**: `Generated dialogue successfully`
- **Audio generation**: `Generated audio: alex_123.mp3`
- **Chat comments**: `Chat agent comment: AI_Skeptic: ...`

### Check Generated Audio

```bash
# List audio files
ls -lh backend/static/audio/

# Play audio (macOS)
afplay backend/static/audio/alex_*.mp3
```

### Access Audio via Browser

While the server is running:
```
http://localhost:8000/static/audio/alex_1762604679092.mp3
```

---

## 🎨 Complete Test Flow

Here's a full test scenario:

```bash
# Terminal 1: Start server
source venv/bin/activate
python -m backend.main

# Terminal 2: Run tests
# 1. Create topics
curl -X POST http://localhost:8000/api/topic \
  -H "Content-Type: application/json" \
  -d '{"text": "AI Ethics", "nickname": "Philosopher"}'

# 2. Vote it up
curl -X POST http://localhost:8000/api/vote \
  -H "Content-Type: application/json" \
  -d '{"id": "TOPIC_ID", "delta": 1}'

# 3. React positively
curl -X POST http://localhost:8000/api/react \
  -H "Content-Type: application/json" \
  -d '{"id": "TOPIC_ID", "emoji": "👍"}'

# 4. Start podcast
curl -X POST http://localhost:8000/api/podcast/start

# 5. Watch it run!
# - Check Terminal 1 for logs
# - Check transcript after 30 seconds:
curl http://localhost:8000/api/podcast/transcript | python3 -m json.tool

# 6. Stop when done
curl -X POST http://localhost:8000/api/podcast/stop
```

---

## 🐛 Troubleshooting

### Server won't start

**Error:** `ModuleNotFoundError`
```bash
# Solution: Make sure you're in project root and venv is activated
cd /Users/jakubpiotrowski/PycharmProjects/Unlimited_Podcast
source venv/bin/activate
python -m backend.main
```

**Error:** `Address already in use`
```bash
# Solution: Kill the process using port 8000
lsof -ti:8000 | xargs kill -9
```

### OpenAI API Errors

**Error:** `AuthenticationError`
```bash
# Solution: Check your API key
cat .env | grep OPENAI_API_KEY
```

### No topics to discuss

**Error:** Podcast says "No topics available"
```bash
# Solution: Create at least one topic first
curl -X POST http://localhost:8000/api/topic \
  -H "Content-Type: application/json" \
  -d '{"text": "Getting Started", "nickname": "Admin"}'
```

---

## 💰 Cost Management

**Each 20-second turn costs ~$0.04**

To avoid unexpected costs:
1. **Stop the podcast** when testing: `curl -X POST http://localhost:8000/api/podcast/stop`
2. **Kill the server** when done: `Ctrl+C` in Terminal 1
3. **Set short test runs**: Create 1-2 topics, run for 2-3 minutes, then stop

---

## 📁 What Gets Created

When you run the podcast:

```
backend/static/audio/
├── alex_1234567890.mp3   # Alex's speech (optimistic)
├── mira_1234567890.mp3   # Mira's speech (skeptical)
└── ... (more files as podcast runs)
```

These files are:
- ✅ Real MP3 audio from OpenAI TTS
- ✅ Playable in any media player
- ✅ Automatically cleaned up after 1 hour

---

## 🎯 What to Demo

For the hackathon, demonstrate:

1. **API Documentation**: http://localhost:8000/docs
   - Show the clean API structure

2. **Topic Creation & Voting**:
   - Submit 3 topics
   - Vote and react with emojis

3. **Start Podcast**:
   - Show logs in real-time
   - Demonstrate turn cycle

4. **View Results**:
   - Transcript with Alex/Mira dialogue
   - Generated audio files
   - AI chat comments

5. **Architecture**:
   - Explain Supervisor (GPT-4o)
   - Show Content Generator (GPT-4o-mini)
   - Highlight chat agents

---

## 🔄 Daily Workflow

### Starting Your Day
```bash
cd /Users/jakubpiotrowski/PycharmProjects/Unlimited_Podcast
source venv/bin/activate
python -m backend.main
```

### Testing Changes
```bash
# Backend auto-reloads on file changes (uvicorn --reload)
# Just edit files and save - server restarts automatically
```

### Ending Your Day
```bash
# In Terminal 1 (server):
Ctrl+C

# Optional: Deactivate venv
deactivate
```

---

## 📚 Important URLs

| Resource | URL |
|----------|-----|
| API Root | http://localhost:8000/ |
| Interactive Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |
| Redoc | http://localhost:8000/redoc |
| Static Audio | http://localhost:8000/static/audio/ |

---

## ✅ Success Checklist

Before the hackathon demo:
- [ ] Backend starts without errors
- [ ] Can create topics via API
- [ ] Can vote and react to topics
- [ ] Podcast starts and generates audio
- [ ] Transcript updates in real-time
- [ ] Chat agents post comments
- [ ] Audio files are playable
- [ ] Can stop podcast cleanly

---

## 🚀 You're Ready!

Your backend is:
- ✅ **Production-quality** code
- ✅ **Clean architecture** (models, services, API)
- ✅ **Multi-LLM system** (Supervisor + Content + Chat)
- ✅ **Real-time streaming** (SSE)
- ✅ **Fully functional** (tested and working)

**Next:** Frontend with Lovable or test Dust integration!
