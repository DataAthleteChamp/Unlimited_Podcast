# 🔌 Frontend-Backend Endpoint Alignment

**Generated:** 2025-11-08
**Status:** ⚠️ INCOMPLETE - Frontend missing many integrations

---

## 📊 Summary

| Category | Backend Endpoints | Frontend Usage | Status |
|----------|-------------------|----------------|--------|
| Topics   | 5 endpoints       | 1 endpoint     | ⚠️ Partial |
| Chat     | 2 endpoints       | 0 endpoints    | ❌ Not Used |
| Podcast  | 5 endpoints       | 0 endpoints    | ❌ Not Used |
| Streaming| 1 endpoint        | 0 endpoints    | ❌ Not Used |

---

## 🎯 TOPICS ENDPOINTS

### ✅ ALIGNED

#### `POST /api/topics/suggestions`
- **Backend:** ✅ Implemented (backend/api/topics.py:132)
- **Frontend:** ✅ Used (src/pages/Index.tsx:30)
- **Purpose:** Generate AI topic suggestions from chat messages
- **Request:**
  ```json
  {
    "messages": [
      {"text": "...", "sender": "...", "timestamp": "..."}
    ]
  }
  ```
- **Response:**
  ```json
  [
    {"id": 1, "title": "...", "description": "...", "votes": 0}
  ]
  ```
- **Status:** ✅ Working

---

### ⚠️ NOT ALIGNED - Backend exists, Frontend doesn't use

#### `POST /api/topic`
- **Backend:** ✅ Implemented (backend/api/topics.py:24)
- **Frontend:** ❌ Not used
- **Purpose:** Create a new topic for voting
- **Request:**
  ```json
  {
    "text": "AI in Healthcare",
    "nickname": "TechFan"
  }
  ```
- **Response:** Topic object with id, votes, reactions
- **Frontend Impact:** Topics generated from suggestions are NOT saved to backend
- **Action Needed:** Frontend should POST topics when user wants to save a suggestion

---

#### `GET /api/topics`
- **Backend:** ✅ Implemented (backend/api/topics.py:120)
- **Frontend:** ❌ Not used
- **Purpose:** Get all topics sorted by score
- **Response:** Array of Topic objects
- **Frontend Impact:** No way to see all community topics
- **Action Needed:** Could be used to show global topic list

---

#### `POST /api/vote`
- **Backend:** ✅ Implemented (backend/api/topics.py:48)
- **Frontend:** ❌ Not used (votes are local only!)
- **Purpose:** Vote on a topic
- **Request:**
  ```json
  {
    "id": "topic-uuid",
    "delta": 1  // or -1
  }
  ```
- **Frontend Impact:** **⚠️ CRITICAL - Votes don't reach backend!**
- **Current Behavior:** Frontend tracks votes locally in state only (Index.tsx:52-76)
- **Action Needed:** Send votes to backend so podcast can use them

---

#### `POST /api/react`
- **Backend:** ✅ Implemented (backend/api/topics.py:77)
- **Frontend:** ❌ Not used
- **Purpose:** Add emoji reactions (👍/👎) to topics
- **Request:**
  ```json
  {
    "id": "topic-uuid",
    "emoji": "👍"
  }
  ```
- **Frontend Impact:** No emoji reactions in UI
- **Action Needed:** Could add this feature to TopicCard

---

## 💬 CHAT ENDPOINTS

### ❌ NOT USED BY FRONTEND

#### `POST /api/chat/message`
- **Backend:** ✅ Implemented (backend/api/chat.py:14)
- **Frontend:** ❌ Not used
- **Purpose:** Send a chat message
- **Current Behavior:** Frontend stores messages locally only (ChatSidebar.tsx:20-44)
- **Frontend Impact:** Messages don't persist or sync between users
- **Action Needed:** Send chat messages to backend

#### `GET /api/chat/messages`
- **Backend:** ✅ Implemented (backend/api/chat.py:51)
- **Frontend:** ❌ Not used
- **Purpose:** Get recent chat messages
- **Frontend Impact:** Can't see other users' messages or history
- **Action Needed:** Fetch messages on load

---

## 🎙️ PODCAST ENDPOINTS

### ❌ NOT USED BY FRONTEND

#### `POST /api/podcast/start`
- **Backend:** ✅ Implemented (backend/api/podcast.py:16)
- **Frontend:** ❌ Not used
- **Purpose:** Start the podcast scheduler
- **Frontend Impact:** **⚠️ CRITICAL - No way to start podcast from UI!**
- **Action Needed:** Add "Start Podcast" button

#### `POST /api/podcast/stop`
- **Backend:** ✅ Implemented (backend/api/podcast.py:31)
- **Frontend:** ❌ Not used
- **Purpose:** Stop the podcast scheduler
- **Action Needed:** Add "Stop Podcast" button

#### `GET /api/podcast/status`
- **Backend:** ✅ Implemented (backend/api/podcast.py:46)
- **Frontend:** ❌ Not used
- **Purpose:** Get current podcast status (running, topic, turn count)
- **Response:**
  ```json
  {
    "running": true,
    "current_topic": "AI Ethics",
    "turn_count": 5,
    "uptime_seconds": 120
  }
  ```
- **Action Needed:** Poll this to show podcast status in UI

#### `GET /api/podcast/transcript`
- **Backend:** ✅ Implemented (backend/api/podcast.py:70)
- **Frontend:** ❌ Not used
- **Purpose:** Get recent transcript entries (what Alex & Mira said)
- **Response:** Array of TranscriptEntry objects
- **Action Needed:** Display transcript below audio visualizer

#### `GET /api/podcast/now`
- **Backend:** ✅ Implemented (backend/api/podcast.py:82)
- **Frontend:** ❌ Not used
- **Purpose:** Get current now playing information (who's speaking, audio URL)
- **Response:**
  ```json
  {
    "topic_id": "...",
    "topic_text": "AI Ethics",
    "speaker": "alex",
    "text": "I think AI ethics is crucial...",
    "audio_url": "/static/audio/alex_123.mp3",
    "started_at": 1699999999,
    "ends_at": 1700000020,
    "turn_number": 5
  }
  ```
- **Frontend Impact:** **⚠️ CRITICAL - No actual audio playback!**
- **Action Needed:** Use this to play real audio files

---

## 🔄 STREAMING ENDPOINT

### ❌ NOT USED BY FRONTEND

#### `GET /api/stream`
- **Backend:** ✅ Implemented (backend/api/stream.py:15)
- **Frontend:** ❌ Not used
- **Purpose:** Server-Sent Events (SSE) for real-time updates
- **Events Sent:**
  - `TOPICS_UPDATED` - When topics/votes change
  - `NOW_PLAYING` - When podcast segment starts playing
  - `TRANSCRIPT_UPDATE` - When new dialogue is added
  - `CHAT_MESSAGE` - When new chat message arrives
- **Frontend Impact:** No real-time updates
- **Action Needed:** Connect EventSource to receive live updates

---

## 🎬 ACTION PLAN

### Priority 1: Make Voting Work (CRITICAL)
1. ✅ Backend has endpoint: `POST /api/vote`
2. ❌ Frontend needs to call it when user votes
3. **File to edit:** `frontend/src/pages/Index.tsx` (handleVote function)

### Priority 2: Start/Stop Podcast (CRITICAL)
1. ✅ Backend has endpoints: `POST /api/podcast/start` and `/stop`
2. ❌ Frontend needs buttons and API calls
3. **File to edit:** `frontend/src/pages/Index.tsx` (add controls)

### Priority 3: Audio Playback (CRITICAL)
1. ✅ Backend generates MP3 files: `GET /api/podcast/now`
2. ❌ Frontend needs `<audio>` element to play them
3. **File to edit:** `frontend/src/components/AudioVisualizer.tsx`

### Priority 4: Real-time Updates (HIGH)
1. ✅ Backend has SSE: `GET /api/stream`
2. ❌ Frontend needs EventSource connection
3. **File to edit:** `frontend/src/pages/Index.tsx` (useEffect for SSE)

### Priority 5: Chat Persistence (MEDIUM)
1. ✅ Backend has: `POST /api/chat/message` and `GET /api/chat/messages`
2. ❌ Frontend needs to sync messages
3. **File to edit:** `frontend/src/components/ChatSidebar.tsx`

### Priority 6: Topic Creation (LOW)
1. ✅ Backend has: `POST /api/topic`
2. ❌ Frontend could save AI suggestions as real topics
3. **File to edit:** `frontend/src/pages/Index.tsx`

---

## 📝 CURRENT FRONTEND API USAGE

**File:** `frontend/src/pages/Index.tsx`

```typescript
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Only 1 endpoint used:
const response = await fetch(`${API_URL}/api/topics/suggestions`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ messages })
});
```

**That's it!** Only 1 out of 13 backend endpoints is being used.

---

## ✅ NEXT STEPS

Run through Option B (test backend) and Option A (implement frontend) to complete the integration.
