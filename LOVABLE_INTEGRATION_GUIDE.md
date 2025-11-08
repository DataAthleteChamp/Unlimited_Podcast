# 🎨 Lovable Frontend Integration Guide

## 🎯 Overview

This guide shows you how to:
1. Generate UI in Lovable
2. Export and set up the frontend
3. Connect it to your FastAPI backend
4. Implement real-time updates with SSE

---

## 📋 Step 1: Generate UI in Lovable

### Go to Lovable.dev

1. Visit https://lovable.dev/
2. Sign in with your account
3. Click "Create New Project"

### Prompt for Lovable

Copy and paste this prompt into Lovable:

```
Create a modern podcast interface called "Endless AI Podcast" with these features:

LAYOUT:
- Header with podcast title and logo
- Three main sections in a responsive grid:
  1. Left sidebar: Topic submission and voting
  2. Center: Now playing podcast player with transcript
  3. Right sidebar: Live community chat

TOPIC SECTION (Left):
- Input field for topic submission with nickname field
- "Submit Topic" button
- List of topics showing:
  - Topic text
  - Nickname of submitter
  - Vote count with up/down buttons
  - Emoji reaction buttons (👍 thumbs up, 👎 thumbs down)
  - Show reaction counts next to emojis
  - Topics sorted by score (votes + weighted reactions)

NOW PLAYING SECTION (Center):
- Current speaker indicator (Alex or Mira)
- Speaker avatar/icon
- Current topic being discussed
- Audio player (HTML5 audio element)
- Live transcript display showing:
  - Speaker name
  - Dialogue text
  - Auto-scroll to latest
  - Different colors for Alex (blue) vs Mira (purple)
- Podcast controls:
  - "Start Podcast" button
  - "Stop Podcast" button
  - Status indicator (running/stopped)

CHAT SECTION (Right):
- Chat messages display with:
  - Nickname
  - Message text
  - Timestamp
  - Different badge/indicator for AI vs human messages
- Chat input field with nickname
- "Send" button
- Auto-scroll to latest messages

STYLING:
- Dark mode theme with podcast vibe
- Tailwind CSS
- shadcn/ui components
- Smooth animations
- Responsive design (mobile-friendly)
- Professional, modern look

COLORS:
- Background: Dark blue/black gradient
- Alex speaker: Blue accent (#3B82F6)
- Mira speaker: Purple accent (#A855F7)
- Accent colors for reactions and votes
```

Lovable will generate a beautiful UI for you!

---

## 📦 Step 2: Export from Lovable

### Export the Code

1. In Lovable, click the **GitHub icon** (top right)
2. Click **"Connect to GitHub"** (if not already connected)
3. Authorize Lovable to access your GitHub
4. Click **"View Code"**
5. Click **"Download ZIP"**

Alternatively:
- Lovable pushes code to a GitHub repo
- You can clone that repo directly

### Extract the Code

```bash
cd /Users/jakubpiotrowski/PycharmProjects/Unlimited_Podcast

# If you downloaded ZIP:
unzip lovable-export.zip -d frontend/

# Or if you cloned from GitHub:
git clone YOUR_LOVABLE_REPO_URL frontend/
```

You should now have:
```
Unlimited_Podcast/
├── backend/          # Your FastAPI backend (already built)
└── frontend/         # Lovable-generated React + Vite
```

---

## 🔧 Step 3: Configure Frontend for Backend

### Install Frontend Dependencies

```bash
cd frontend
npm install
```

### Create API Configuration

Create `frontend/src/config/api.ts`:

```typescript
// API Configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  SSE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
};

export const API_ENDPOINTS = {
  // Topics
  TOPICS: '/api/topics',
  CREATE_TOPIC: '/api/topic',
  VOTE: '/api/vote',
  REACT: '/api/react',

  // Podcast
  PODCAST_START: '/api/podcast/start',
  PODCAST_STOP: '/api/podcast/stop',
  PODCAST_STATUS: '/api/podcast/status',
  PODCAST_TRANSCRIPT: '/api/podcast/transcript',

  // Chat
  CHAT_MESSAGES: '/api/chat/messages',
  SEND_MESSAGE: '/api/chat/message',

  // Streaming
  STREAM: '/api/stream',
};
```

### Create Environment File

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

---

## 🔌 Step 4: Create API Client

Create `frontend/src/services/api.ts`:

```typescript
import { API_CONFIG, API_ENDPOINTS } from '../config/api';

// Types
export interface Topic {
  id: string;
  text: string;
  nickname: string;
  votes: number;
  reactions_thumbs_up: number;
  reactions_thumbs_down: number;
  created_at: number;
}

export interface ChatMessage {
  id: string;
  nickname: string;
  message: string;
  is_ai: boolean;
  persona?: string;
  timestamp: number;
}

export interface TranscriptEntry {
  speaker: string;
  text: string;
  timestamp: number;
  turn_number: number;
}

export interface PodcastStatus {
  running: boolean;
  current_topic?: string;
  turn_count: number;
  uptime_seconds: number;
}

// API Client Class
class APIClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_CONFIG.BASE_URL;
  }

  // Generic fetch wrapper
  private async fetch<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  }

  // Topics
  async getTopics(): Promise<Topic[]> {
    return this.fetch<Topic[]>(API_ENDPOINTS.TOPICS);
  }

  async createTopic(text: string, nickname: string): Promise<Topic> {
    return this.fetch<Topic>(API_ENDPOINTS.CREATE_TOPIC, {
      method: 'POST',
      body: JSON.stringify({ text, nickname }),
    });
  }

  async voteTopic(id: string, delta: number): Promise<Topic> {
    return this.fetch<Topic>(API_ENDPOINTS.VOTE, {
      method: 'POST',
      body: JSON.stringify({ id, delta }),
    });
  }

  async reactToTopic(id: string, emoji: string): Promise<Topic> {
    return this.fetch<Topic>(API_ENDPOINTS.REACT, {
      method: 'POST',
      body: JSON.stringify({ id, emoji }),
    });
  }

  // Podcast
  async startPodcast(): Promise<{ status: string; message: string }> {
    return this.fetch(API_ENDPOINTS.PODCAST_START, { method: 'POST' });
  }

  async stopPodcast(): Promise<{ status: string; message: string }> {
    return this.fetch(API_ENDPOINTS.PODCAST_STOP, { method: 'POST' });
  }

  async getPodcastStatus(): Promise<PodcastStatus> {
    return this.fetch<PodcastStatus>(API_ENDPOINTS.PODCAST_STATUS);
  }

  async getTranscript(): Promise<TranscriptEntry[]> {
    return this.fetch<TranscriptEntry[]>(API_ENDPOINTS.PODCAST_TRANSCRIPT);
  }

  // Chat
  async getChatMessages(): Promise<ChatMessage[]> {
    return this.fetch<ChatMessage[]>(API_ENDPOINTS.CHAT_MESSAGES);
  }

  async sendChatMessage(
    nickname: string,
    message: string
  ): Promise<ChatMessage> {
    return this.fetch<ChatMessage>(API_ENDPOINTS.SEND_MESSAGE, {
      method: 'POST',
      body: JSON.stringify({ nickname, message }),
    });
  }
}

export const api = new APIClient();
```

---

## 📡 Step 5: Implement SSE (Real-Time Updates)

Create `frontend/src/hooks/useSSE.ts`:

```typescript
import { useEffect, useRef, useState } from 'react';
import { API_CONFIG, API_ENDPOINTS } from '../config/api';

// SSE Event types
export interface SSEEvent {
  event: string;
  data: any;
}

export function useSSE(onEvent: (event: SSEEvent) => void) {
  const [connected, setConnected] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    // Create SSE connection
    const eventSource = new EventSource(
      `${API_CONFIG.SSE_URL}${API_ENDPOINTS.STREAM}`
    );

    eventSourceRef.current = eventSource;

    // Connection opened
    eventSource.onopen = () => {
      console.log('✅ SSE connected');
      setConnected(true);
    };

    // Handle all events
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onEvent({ event: 'message', data });
      } catch (error) {
        console.error('Error parsing SSE message:', error);
      }
    };

    // Handle specific event types
    eventSource.addEventListener('TOPICS_UPDATED', (event: any) => {
      try {
        const data = JSON.parse(event.data);
        onEvent({ event: 'TOPICS_UPDATED', data });
      } catch (error) {
        console.error('Error parsing TOPICS_UPDATED:', error);
      }
    });

    eventSource.addEventListener('NOW_PLAYING', (event: any) => {
      try {
        const data = JSON.parse(event.data);
        onEvent({ event: 'NOW_PLAYING', data });
      } catch (error) {
        console.error('Error parsing NOW_PLAYING:', error);
      }
    });

    eventSource.addEventListener('TRANSCRIPT_UPDATE', (event: any) => {
      try {
        const data = JSON.parse(event.data);
        onEvent({ event: 'TRANSCRIPT_UPDATE', data });
      } catch (error) {
        console.error('Error parsing TRANSCRIPT_UPDATE:', error);
      }
    });

    eventSource.addEventListener('CHAT_MESSAGE', (event: any) => {
      try {
        const data = JSON.parse(event.data);
        onEvent({ event: 'CHAT_MESSAGE', data });
      } catch (error) {
        console.error('Error parsing CHAT_MESSAGE:', error);
      }
    });

    // Handle errors
    eventSource.onerror = (error) => {
      console.error('❌ SSE error:', error);
      setConnected(false);
    };

    // Cleanup on unmount
    return () => {
      eventSource.close();
      console.log('🔌 SSE disconnected');
    };
  }, [onEvent]);

  return { connected };
}
```

---

## 🎯 Step 6: Example Component Integration

Here's an example of how to use the API client and SSE in your components:

### Example: Topic List Component

```typescript
import { useEffect, useState } from 'react';
import { api, Topic } from '../services/api';
import { useSSE } from '../hooks/useSSE';

export function TopicList() {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [nickname, setNickname] = useState('');
  const [topicText, setTopicText] = useState('');

  // Load initial topics
  useEffect(() => {
    api.getTopics().then(setTopics);
  }, []);

  // Listen for real-time updates
  useSSE((event) => {
    if (event.event === 'TOPICS_UPDATED') {
      setTopics(event.data.topics);
    }
  });

  // Create topic
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.createTopic(topicText, nickname);
    setTopicText('');
  };

  // Vote
  const handleVote = async (id: string, delta: number) => {
    await api.voteTopic(id, delta);
  };

  // React
  const handleReact = async (id: string, emoji: string) => {
    await api.reactToTopic(id, emoji);
  };

  return (
    <div>
      {/* Topic submission form */}
      <form onSubmit={handleSubmit}>
        <input
          value={nickname}
          onChange={(e) => setNickname(e.target.value)}
          placeholder="Your nickname"
        />
        <input
          value={topicText}
          onChange={(e) => setTopicText(e.target.value)}
          placeholder="Topic idea"
        />
        <button type="submit">Submit Topic</button>
      </form>

      {/* Topic list */}
      {topics.map((topic) => (
        <div key={topic.id}>
          <h3>{topic.text}</h3>
          <p>by {topic.nickname}</p>

          {/* Voting */}
          <button onClick={() => handleVote(topic.id, 1)}>👍 {topic.votes}</button>
          <button onClick={() => handleVote(topic.id, -1)}>👎</button>

          {/* Reactions */}
          <button onClick={() => handleReact(topic.id, '👍')}>
            👍 {topic.reactions_thumbs_up}
          </button>
          <button onClick={() => handleReact(topic.id, '👎')}>
            👎 {topic.reactions_thumbs_down}
          </button>
        </div>
      ))}
    </div>
  );
}
```

### Example: Podcast Player Component

```typescript
import { useEffect, useState, useRef } from 'react';
import { api } from '../services/api';
import { useSSE } from '../hooks/useSSE';

export function PodcastPlayer() {
  const [isRunning, setIsRunning] = useState(false);
  const [currentSpeaker, setCurrentSpeaker] = useState('');
  const [currentText, setCurrentText] = useState('');
  const audioRef = useRef<HTMLAudioElement>(null);

  // Listen for real-time updates
  useSSE((event) => {
    if (event.event === 'NOW_PLAYING') {
      setCurrentSpeaker(event.data.speaker);
      setCurrentText(event.data.text);

      // Play audio
      if (audioRef.current && event.data.audio_url) {
        audioRef.current.src = `http://localhost:8000${event.data.audio_url}`;
        audioRef.current.play();
      }
    }
  });

  const handleStart = async () => {
    await api.startPodcast();
    setIsRunning(true);
  };

  const handleStop = async () => {
    await api.stopPodcast();
    setIsRunning(false);
  };

  return (
    <div>
      <h2>Now Playing</h2>

      {/* Controls */}
      <button onClick={handleStart} disabled={isRunning}>
        Start Podcast
      </button>
      <button onClick={handleStop} disabled={!isRunning}>
        Stop Podcast
      </button>

      {/* Current speaker */}
      <div>
        <h3>{currentSpeaker}</h3>
        <p>{currentText}</p>
      </div>

      {/* Audio player */}
      <audio ref={audioRef} controls />
    </div>
  );
}
```

---

## 🚀 Step 7: Run Full Stack

### Terminal 1: Start Backend

```bash
cd /Users/jakubpiotrowski/PycharmProjects/Unlimited_Podcast
source venv/bin/activate
python -m backend.main
```

Backend running on: `http://localhost:8000`

### Terminal 2: Start Frontend

```bash
cd /Users/jakubpiotrowski/PycharmProjects/Unlimited_Podcast/frontend
npm run dev
```

Frontend running on: `http://localhost:5173`

### Open Browser

Visit: `http://localhost:5173`

You should see:
- ✅ Topic submission working
- ✅ Voting and reactions working
- ✅ Podcast player working
- ✅ Real-time updates via SSE
- ✅ Chat messages appearing

---

## 🎨 Customizing Lovable UI

If Lovable's initial design needs tweaks, you can:

1. **Edit in Lovable**: Describe changes, regenerate
2. **Edit exported code**: Modify React components directly
3. **Use shadcn/ui**: Add more components from shadcn

### Common Customizations

**Change colors:**
```typescript
// frontend/tailwind.config.js
theme: {
  extend: {
    colors: {
      alex: '#3B82F6',    // Blue for Alex
      mira: '#A855F7',    // Purple for Mira
    }
  }
}
```

**Add custom components:**
```bash
# In frontend directory
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add badge
```

---

## 📊 Full Integration Checklist

- [ ] Lovable UI generated
- [ ] Code exported and extracted to `frontend/`
- [ ] Dependencies installed (`npm install`)
- [ ] API client created (`services/api.ts`)
- [ ] SSE hook implemented (`hooks/useSSE.ts`)
- [ ] Environment configured (`.env`)
- [ ] Components connected to API
- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Real-time updates working
- [ ] Audio playback working
- [ ] Chat integration working

---

## 🐛 Troubleshooting

### CORS Errors

**Error:** `Access-Control-Allow-Origin`

**Solution:** Backend already configured with CORS. Make sure backend is running.

### SSE Not Connecting

**Error:** EventSource connection fails

**Solution:**
```typescript
// Check the URL is correct
console.log('SSE URL:', `${API_CONFIG.SSE_URL}${API_ENDPOINTS.STREAM}`);

// Should be: http://localhost:8000/api/stream
```

### Audio Not Playing

**Error:** Audio doesn't play automatically

**Solution:**
```typescript
// Most browsers block autoplay. Add user interaction:
audioRef.current.play().catch(error => {
  console.log('Autoplay blocked. User must click play.');
});
```

---

## 💡 Pro Tips

1. **Use React Query**: For better data fetching
   ```bash
   npm install @tanstack/react-query
   ```

2. **Add Loading States**: Show spinners while loading
3. **Error Handling**: Display friendly error messages
4. **Optimistic UI**: Update UI before API responds
5. **Audio Queue**: Queue multiple audio segments

---

## 📚 Summary

You now have:
- ✅ **Backend API** (FastAPI, Python)
- ✅ **Frontend UI** (React + Vite, Lovable)
- ✅ **Real-time communication** (SSE)
- ✅ **Audio playback** (OpenAI TTS)
- ✅ **Complete integration**

**Your full stack podcast platform is ready for the hackathon!** 🎉
