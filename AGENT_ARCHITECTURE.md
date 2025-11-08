# Agent Architecture Summary

## 🎯 Quick Answer

### Python Agents (What We Have)
```
5 Python Services calling OpenAI directly:

1. supervisor.py           → GPT-4o (Supervisor)
2. content_generator.py    → GPT-4o-mini (Dialogue Writer)
3. chat_agents.py          → GPT-4o-mini × 3 (Enthusiast, Skeptic, Curious)
4. tts_service.py          → OpenAI TTS (not an LLM)
```

### Dust Agents (What to Create in Dust UI)
```
3 Agents to create at dust.tt:

1. "podcast-supervisor"        → GPT-4o
2. "podcast-dialogue-writer"   → GPT-4o-mini
3. "podcast-chat-agent"        → GPT-4o-mini
```

---

## 📋 Agent Mapping

| Python Service | Dust Agent | Model | Purpose |
|----------------|------------|-------|---------|
| `supervisor.py` | `podcast-supervisor` | GPT-4o | Topic selection |
| `content_generator.py` | `podcast-dialogue-writer` | GPT-4o-mini | Write Alex & Mira dialogue |
| `chat_agents.py` (3x) | `podcast-chat-agent` | GPT-4o-mini | Generate community comments |
| `tts_service.py` | N/A | OpenAI TTS | Convert text to speech |

---

## 🔧 How It Works

### Mode 1: Direct OpenAI (Default)
```
User submits topic
  ↓
Python: supervisor.py calls OpenAI GPT-4o directly
  ↓
Selects topic
  ↓
Python: content_generator.py calls OpenAI GPT-4o-mini
  ↓
Generates dialogue
  ↓
Python: tts_service.py calls OpenAI TTS
  ↓
Creates audio
```

### Mode 2: With Dust (Enhanced)
```
User submits topic
  ↓
Python: dust_client.py calls Dust agent "podcast-supervisor"
  ↓
Dust: Uses GPT-4o, manages context
  ↓
Returns decision
  ↓
Python: dust_client.py calls Dust agent "podcast-dialogue-writer"
  ↓
Dust: Uses GPT-4o-mini, maintains conversation memory
  ↓
Returns dialogue
  ↓
Python: tts_service.py calls OpenAI TTS (same as Mode 1)
  ↓
Creates audio
```

---

## 🎨 Prompts for Dust Agents

### Agent 1: podcast-supervisor

**System Prompt:**
```
You are the Supervisor AI for the "Endless AI Podcast".

Make strategic decisions about which topic to discuss next.

Decision rules:
1. If current topic has ≥70% positive reactions: consider continuing
2. If current topic has 3+ turns: likely switch
3. Otherwise: switch to highest-scored topic

Always respond with JSON:
{
  "decision": "continue" or "switch",
  "selected_topic": "exact topic text",
  "reasoning": "brief explanation",
  "context_for_next_turn": "context for dialogue"
}
```

**Model:** GPT-4o
**Temperature:** 0.7
**Max Tokens:** 500

---

### Agent 2: podcast-dialogue-writer

**System Prompt:**
```
You are a podcast dialogue writer.

Create conversation between:
- Alex: Optimistic, forward-thinking (speaks first)
- Mira: Skeptical, pragmatic (responds)

Requirements:
- Each speaks 2-3 sentences (max 100 words)
- Different perspectives but respectful
- Conversational and engaging

Always respond with JSON:
{
  "alex": "dialogue here",
  "mira": "response here",
  "summary": "one sentence summary"
}
```

**Model:** GPT-4o-mini
**Temperature:** 0.8
**Max Tokens:** 400

---

### Agent 3: podcast-chat-agent

**System Prompt:**
```
You are a podcast community member.

Personas (assigned via input):
- Enthusiast: Positive, excited
- Skeptic: Critical, questioning
- Curious: Neutral, inquisitive

Generate SHORT comments (10-20 words) that:
- React to specific dialogue points
- Match persona personality
- Feel authentic

Respond with ONLY the comment text.
```

**Model:** GPT-4o-mini
**Temperature:** 0.9
**Max Tokens:** 60

---

## 🚀 Current Status

✅ **Python Backend:** Complete and working
✅ **Direct OpenAI:** Fully functional
✅ **Dust Integration Code:** Ready (`dust_client.py`)
⏳ **Dust Agents:** Need to be created in Dust UI

---

## 📝 Action Items

### To Use Direct OpenAI (Works Now):
```bash
# In .env:
ENABLE_DUST=false

# Run:
python -m backend.main
```

### To Add Dust Integration:
1. Go to https://dust.tt/
2. Create 3 agents with prompts above
3. Copy agent IDs
4. Update `.env`:
   ```env
   ENABLE_DUST=true
   DUST_AGENT_SUPERVISOR_ID=agent_xxxxx
   DUST_AGENT_CONTENT_ID=agent_yyyyy
   DUST_AGENT_CHAT_ID=agent_zzzzz
   ```
5. Update `backend/services/dust_client.py` with IDs
6. Run: `python -m backend.main`

See `DUST_SETUP_GUIDE.md` for detailed instructions.

---

## 💡 Key Insight

**You don't need Dust to run the podcast!**

The Python backend works perfectly with direct OpenAI calls. Dust is an **enhancement** that provides:
- Better context management
- Conversation memory
- Orchestration layer
- Partner tool requirement ✓

But the system falls back gracefully if Dust isn't configured.

---

## 🎯 For Hackathon Demo

**Minimum (works immediately):**
- Use direct OpenAI
- Skip Dust setup
- Still very impressive

**Ideal (shows full stack):**
- Create Dust agents
- Enable Dust integration
- Show multi-layer orchestration
- Fulfill all partner requirements

Both approaches are valid! Choose based on time available.
