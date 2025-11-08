# Two-Repository Integration Guide

## Repository Setup

You have **two separate repositories**:

### Backend Repository
- **Repo**: `Unlimited_Podcast` (this repo)
- **Tech**: Python/FastAPI
- **Port**: 8000
- **Location**: `/Users/jakubpiotrowski/PycharmProjects/Unlimited_Podcast`

### Frontend Repository
- **Repo**: https://github.com/Oszio/endlesspodcast.git
- **Tech**: React/Vite (from Lovable)
- **Port**: 5173
- **Location**: `/Users/jakubpiotrowski/PycharmProjects/endlesspodcast`

## Setup Instructions

### Step 1: Clone Frontend Repository

```bash
# Go to your projects directory
cd /Users/jakubpiotrowski/PycharmProjects

# Clone the frontend repo
git clone https://github.com/Oszio/endlesspodcast.git

# Now you have both:
# - Unlimited_Podcast/ (backend)
# - endlesspodcast/ (frontend)
```

### Step 2: Configure Frontend to Connect to Backend

Create `endlesspodcast/.env.local`:

```bash
# Backend API URL (development)
VITE_API_URL=http://localhost:8000

# Backend API URL (production - when deployed)
# VITE_API_URL=https://your-backend-url.com
```

### Step 3: Update Frontend Vite Config

Edit `endlesspodcast/vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Proxy API requests to backend during development
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/static': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

### Step 4: Update Backend CORS Settings

Make sure your backend allows requests from the frontend.

In `Unlimited_Podcast/.env`:

```bash
# Add frontend URL to CORS origins
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

This is already configured in your backend!

### Step 5: Install Frontend Dependencies

```bash
cd /Users/jakubpiotroski/PycharmProjects/endlesspodcast
npm install
```

## Running Both Servers

### Terminal 1: Backend

```bash
cd /Users/jakubpiotroski/PycharmProjects/Unlimited_Podcast
source venv/bin/activate
python -m backend.main
```

**Backend will run on**: http://localhost:8000

### Terminal 2: Frontend

```bash
cd /Users/jakubpiotroski/PycharmProjects/endlesspodcast
npm run dev
```

**Frontend will run on**: http://localhost:5173

### Test the Integration

1. Open http://localhost:5173 in your browser
2. Frontend should be able to:
   - Call `/api/topics` to get topics
   - Call `/api/topic` to create topics
   - Connect to `/api/stream` for SSE updates
   - Play audio from `/static/audio/`

## Frontend API Integration Code

The frontend needs to connect to your backend. Here's the API client code:

### Create `endlesspodcast/src/lib/api.ts`

```typescript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface Topic {
  id: string;
  text: string;
  nickname: string;
  votes: number;
  reactions_thumbs_up: number;
  reactions_thumbs_down: number;
  score: number;
  created_at: string;
}

export interface TranscriptEntry {
  speaker: string;
  text: string;
  turn_number: number;
  timestamp: string;
}

export interface ChatMessage {
  nickname: string;
  message: string;
  is_ai: boolean;
  persona?: string;
  timestamp: string;
}

export interface PodcastStatus {
  running: boolean;
  turn_number: number;
  current_topic_id: string | null;
}

class PodcastAPI {
  private baseURL: string;

  constructor() {
    this.baseURL = API_URL;
  }

  // Topics
  async getTopics(): Promise<Topic[]> {
    const response = await fetch(`${this.baseURL}/api/topics`);
    if (!response.ok) throw new Error('Failed to fetch topics');
    return response.json();
  }

  async createTopic(text: string, nickname: string): Promise<Topic> {
    const response = await fetch(`${this.baseURL}/api/topic`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, nickname }),
    });
    if (!response.ok) throw new Error('Failed to create topic');
    return response.json();
  }

  async voteTopic(id: string, delta: number): Promise<Topic> {
    const response = await fetch(`${this.baseURL}/api/vote`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id, delta }),
    });
    if (!response.ok) throw new Error('Failed to vote');
    return response.json();
  }

  async reactToTopic(id: string, emoji: '👍' | '👎'): Promise<Topic> {
    const response = await fetch(`${this.baseURL}/api/react`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id, emoji }),
    });
    if (!response.ok) throw new Error('Failed to react');
    return response.json();
  }

  // Podcast
  async startPodcast(): Promise<{ status: string }> {
    const response = await fetch(`${this.baseURL}/api/podcast/start`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to start podcast');
    return response.json();
  }

  async stopPodcast(): Promise<{ status: string }> {
    const response = await fetch(`${this.baseURL}/api/podcast/stop`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to stop podcast');
    return response.json();
  }

  async getPodcastStatus(): Promise<PodcastStatus> {
    const response = await fetch(`${this.baseURL}/api/podcast/status`);
    if (!response.ok) throw new Error('Failed to get status');
    return response.json();
  }

  async getTranscript(): Promise<TranscriptEntry[]> {
    const response = await fetch(`${this.baseURL}/api/podcast/transcript`);
    if (!response.ok) throw new Error('Failed to get transcript');
    return response.json();
  }

  async getNowPlaying() {
    const response = await fetch(`${this.baseURL}/api/podcast/now`);
    if (!response.ok) throw new Error('Failed to get now playing');
    return response.json();
  }

  // Chat
  async getChatMessages(): Promise<ChatMessage[]> {
    const response = await fetch(`${this.baseURL}/api/chat/messages`);
    if (!response.ok) throw new Error('Failed to get chat messages');
    return response.json();
  }

  async sendChatMessage(nickname: string, message: string): Promise<ChatMessage> {
    const response = await fetch(`${this.baseURL}/api/chat/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nickname, message }),
    });
    if (!response.ok) throw new Error('Failed to send message');
    return response.json();
  }

  // SSE Stream
  createEventSource(): EventSource {
    return new EventSource(`${this.baseURL}/api/stream`);
  }
}

export const api = new PodcastAPI();
```

### Create `endlesspodcast/src/hooks/useSSE.ts`

```typescript
import { useEffect, useState } from 'react';
import { api } from '../lib/api';

export function useSSE() {
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const eventSource = api.createEventSource();

    eventSource.onopen = () => {
      console.log('SSE connected');
      setConnected(true);
    };

    eventSource.addEventListener('TOPICS_UPDATED', (event) => {
      const data = JSON.parse(event.data);
      console.log('Topics updated:', data);
      // Trigger re-fetch or update state
      window.dispatchEvent(new CustomEvent('topics-updated', { detail: data }));
    });

    eventSource.addEventListener('NOW_PLAYING', (event) => {
      const data = JSON.parse(event.data);
      console.log('Now playing:', data);
      window.dispatchEvent(new CustomEvent('now-playing', { detail: data }));
    });

    eventSource.addEventListener('TRANSCRIPT_UPDATE', (event) => {
      const data = JSON.parse(event.data);
      console.log('Transcript update:', data);
      window.dispatchEvent(new CustomEvent('transcript-update', { detail: data }));
    });

    eventSource.addEventListener('CHAT_MESSAGE', (event) => {
      const data = JSON.parse(event.data);
      console.log('Chat message:', data);
      window.dispatchEvent(new CustomEvent('chat-message', { detail: data }));
    });

    eventSource.onerror = (error) => {
      console.error('SSE error:', error);
      setConnected(false);
    };

    return () => {
      eventSource.close();
    };
  }, []);

  return { connected };
}
```

## Development Workflow

### Daily Workflow

**Start both servers every time you work:**

```bash
# Terminal 1: Backend
cd ~/PycharmProjects/Unlimited_Podcast
source venv/bin/activate
python -m backend.main

# Terminal 2: Frontend
cd ~/PycharmProjects/endlesspodcast
npm run dev
```

### Making Changes

**Backend changes:**
```bash
cd ~/PycharmProjects/Unlimited_Podcast
# Edit files in backend/
# Server auto-reloads
git add .
git commit -m "feat: add new endpoint"
git push origin main
```

**Frontend changes:**
```bash
cd ~/PycharmProjects/endlesspodcast
# Edit files in src/
# Vite hot-reloads
git add .
git commit -m "feat: add topic voting UI"
git push origin main
```

### Syncing Changes

If backend API changes (new endpoints, modified responses):

1. **Update backend** → Push changes
2. **Update frontend** API client (`src/lib/api.ts`)
3. **Test integration** → Both servers running
4. **Push frontend** changes

## Deployment

### Option 1: Separate Deployments (Recommended)

**Backend:**
- Deploy to Railway/Render/Fly.io
- Get URL: `https://podcast-api.railway.app`

**Frontend:**
- Deploy to Vercel/Netlify/Cloudflare Pages
- Set environment variable:
  ```
  VITE_API_URL=https://podcast-api.railway.app
  ```

**Update CORS on backend** (in `.env`):
```bash
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:5173
```

### Option 2: Same Domain (Advanced)

Use a reverse proxy (nginx/Cloudflare) to serve both from same domain:
- `https://podcast.com/` → Frontend
- `https://podcast.com/api/` → Backend
- `https://podcast.com/static/` → Backend

## Directory Structure

```
/Users/jakubpiotrowski/PycharmProjects/
├── Unlimited_Podcast/          # Backend repo
│   ├── backend/
│   ├── .env
│   ├── .gitignore
│   ├── requirements.txt
│   └── README.md
│
└── endlesspodcast/             # Frontend repo
    ├── src/
    │   ├── components/
    │   ├── hooks/
    │   │   └── useSSE.ts
    │   ├── lib/
    │   │   └── api.ts
    │   └── App.tsx
    ├── public/
    ├── .env.local
    ├── package.json
    ├── vite.config.ts
    └── README.md
```

## Testing the Integration

### 1. Health Check

**Backend:**
```bash
curl http://localhost:8000/health
```

**Frontend:**
Open browser: http://localhost:5173

### 2. Test API Connection

**From frontend console:**
```javascript
fetch('http://localhost:8000/api/topics')
  .then(r => r.json())
  .then(console.log)
```

### 3. Test SSE Connection

**Check browser console** for:
```
SSE connected
```

### 4. Full Integration Test

1. Create topic via frontend UI
2. Backend receives request
3. SSE pushes update
4. Frontend updates live
5. Start podcast
6. Audio plays
7. Transcript updates
8. Chat messages appear

## Troubleshooting

### CORS Errors

**Error:** `blocked by CORS policy`

**Solution:** Update backend `.env`:
```bash
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Restart backend server.

### Cannot Connect to Backend

**Error:** `Failed to fetch` or `ERR_CONNECTION_REFUSED`

**Check:**
1. Is backend running? `curl http://localhost:8000/health`
2. Is it on port 8000? `lsof -ti:8000`
3. Is frontend pointing to right URL? Check `.env.local`

### SSE Not Working

**Error:** EventSource fails to connect

**Check:**
1. CORS is configured correctly
2. `/api/stream` endpoint is accessible
3. Browser DevTools → Network → EventSource connection

### Audio Not Playing

**Error:** 404 on audio files

**Solution:** Make sure backend is serving static files:
```python
# In backend/main.py (already configured)
app.mount("/static", StaticFiles(directory="backend/static"))
```

## Quick Reference

| Task | Backend Command | Frontend Command |
|------|----------------|------------------|
| Start server | `python -m backend.main` | `npm run dev` |
| Install deps | `pip install -r requirements.txt` | `npm install` |
| Run tests | `pytest` | `npm test` |
| Build | N/A | `npm run build` |
| Logs | Terminal output | Browser console |

## Success Checklist

- [ ] Backend repo cloned and running on port 8000
- [ ] Frontend repo cloned and running on port 5173
- [ ] Frontend `.env.local` points to `http://localhost:8000`
- [ ] Backend CORS includes `http://localhost:5173`
- [ ] Can create topics from frontend
- [ ] Topics appear in real-time (SSE working)
- [ ] Can start/stop podcast
- [ ] Audio plays correctly
- [ ] Transcript updates live
- [ ] Chat messages work
- [ ] No CORS errors in browser console

## Benefits of Two-Repo Setup

✅ **Independent deployment** - Deploy backend/frontend separately
✅ **Different teams** - Frontend and backend teams work independently
✅ **Easier CI/CD** - Separate pipelines for each repo
✅ **Clearer boundaries** - Clean separation of concerns
✅ **Flexible scaling** - Scale frontend/backend independently

---

**You're using a multi-repo setup!** 🎉

Both repos work together seamlessly via REST API and SSE.
