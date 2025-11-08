# UI Speaker Parameters Guide

This document explains how to identify which agent is speaking in the UI for animations.

## 🎯 Key Parameter: `speaker`

The **`speaker`** parameter is the main field you need to check to determine who is currently speaking. It will be either:
- `"Alex"` - Optimistic Visionary host
- `"Mira"` - Skeptical Pragmatist host

## 📡 Method 1: Server-Sent Events (SSE) - Real-time Updates

### Event: `NOW_PLAYING`

Listen to the SSE stream at `/api/stream` and watch for the `NOW_PLAYING` event.

**Event Data Structure:**
```json
{
  "speaker": "Alex",           // ← Use this for animations!
  "text": "Dialogue text here",
  "audio_url": "/static/audio/alex_123456.mp3",
  "topic_id": "topic-uuid",
  "topic": "Topic text",
  "turn_number": 1
}
```

**Example JavaScript/TypeScript:**
```javascript
const eventSource = new EventSource('/api/stream');

eventSource.addEventListener('NOW_PLAYING', (event) => {
  const data = JSON.parse(event.data);
  const speaker = data.speaker; // "Alex" or "Mira"
  
  // Add your animation logic here
  if (speaker === "Alex") {
    // Animate Alex avatar/indicator
    animateAlex();
  } else if (speaker === "Mira") {
    // Animate Mira avatar/indicator
    animateMira();
  }
});
```

## 🔄 Method 2: REST API Endpoint - Poll Current State

### Endpoint: `GET /api/podcast/now`

Get the current "now playing" state via REST API.

**Response:**
```json
{
  "topic_id": "topic-uuid",
  "topic_text": "Topic text",
  "speaker": "Alex",           // ← Use this for animations!
  "text": "Dialogue text",
  "audio_url": "/static/audio/alex_123456.mp3",
  "started_at": 1234567890.0,
  "ends_at": 1234567910.0,
  "turn_number": 1
}
```

**Example JavaScript/TypeScript:**
```javascript
async function getCurrentSpeaker() {
  const response = await fetch('/api/podcast/now');
  const nowPlaying = await response.json();
  
  if (nowPlaying) {
    const speaker = nowPlaying.speaker; // "Alex" or "Mira"
    
    // Update UI based on speaker
    updateSpeakerAnimation(speaker);
  }
}

// Poll every second (or use SSE for real-time)
setInterval(getCurrentSpeaker, 1000);
```

## 🎨 UI Animation Examples

### Example 1: Conditional CSS Classes
```javascript
// In your React/Vue/etc component
const [currentSpeaker, setCurrentSpeaker] = useState(null);

eventSource.addEventListener('NOW_PLAYING', (event) => {
  const data = JSON.parse(event.data);
  setCurrentSpeaker(data.speaker);
});

// In JSX/HTML
<div className={`speaker-alex ${currentSpeaker === 'Alex' ? 'active' : ''}`}>
  <img src="/alex-avatar.png" />
</div>
<div className={`speaker-mira ${currentSpeaker === 'Mira' ? 'active' : ''}`}>
  <img src="/mira-avatar.png" />
</div>
```

### Example 2: CSS Animations
```css
.speaker-alex.active {
  animation: pulse 1s infinite;
  border: 3px solid #4CAF50;
}

.speaker-mira.active {
  animation: pulse 1s infinite;
  border: 3px solid #FF9800;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}
```

### Example 3: React Hook
```javascript
function useCurrentSpeaker() {
  const [speaker, setSpeaker] = useState(null);
  
  useEffect(() => {
    const eventSource = new EventSource('/api/stream');
    
    eventSource.addEventListener('NOW_PLAYING', (event) => {
      const data = JSON.parse(event.data);
      setSpeaker(data.speaker);
    });
    
    return () => eventSource.close();
  }, []);
  
  return speaker; // Returns "Alex", "Mira", or null
}

// Usage
function PodcastUI() {
  const currentSpeaker = useCurrentSpeaker();
  
  return (
    <div>
      <div className={currentSpeaker === 'Alex' ? 'speaking' : ''}>
        Alex Avatar
      </div>
      <div className={currentSpeaker === 'Mira' ? 'speaking' : ''}>
        Mira Avatar
      </div>
    </div>
  );
}
```

## 📋 Complete Event Data Fields

When you receive a `NOW_PLAYING` event, you get:

| Field | Type | Description |
|-------|------|-------------|
| `speaker` | `string` | **"Alex" or "Mira"** - Use this for animations! |
| `text` | `string` | The dialogue text being spoken |
| `audio_url` | `string` | URL to the audio file |
| `topic_id` | `string` | ID of the current topic |
| `topic` | `string` | Text of the current topic |
| `turn_number` | `number` | Turn number in sequence |

## 🎯 Quick Reference

**For animations, check:**
```javascript
if (data.speaker === "Alex") {
  // Alex is speaking - animate Alex
}
if (data.speaker === "Mira") {
  // Mira is speaking - animate Mira
}
```

**SSE Event Stream:**
- Endpoint: `/api/stream`
- Event Type: `NOW_PLAYING`
- Key Field: `data.speaker`

**REST API:**
- Endpoint: `GET /api/podcast/now`
- Key Field: `speaker`

## 🔍 Additional Context

- **Alex** uses voice: `"alloy"` (OpenAI TTS)
- **Mira** uses voice: `"onyx"` (OpenAI TTS)
- Audio files are named: `alex_*.mp3` or `mira_*.mp3`
- Speakers alternate: Alex speaks first, then Mira, in each turn

