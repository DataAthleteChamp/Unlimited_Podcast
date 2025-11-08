# Dust.tt Setup Guide for Endless AI Podcast

## 🎯 Overview

This guide shows you exactly what agents to create in Dust and how to integrate them with the Python backend.

## 🤖 Agent Comparison

### Current Python Architecture (Working Now)
```
✅ Direct OpenAI API calls (no Dust needed to start)

backend/services/supervisor.py          → GPT-4o directly
backend/services/content_generator.py   → GPT-4o-mini directly
backend/services/chat_agents.py         → GPT-4o-mini directly (3x)
```

### Enhanced with Dust (Optional Upgrade)
```
🎯 Dust orchestration (better context management)

backend/services/dust_client.py → Calls Dust agents
  ├── Dust: podcast-supervisor → GPT-4o
  ├── Dust: podcast-dialogue-writer → GPT-4o-mini
  └── Dust: podcast-chat-agent → GPT-4o-mini
```

**Benefit:** Dust provides better conversation memory and orchestration.

---

## 📋 Step-by-Step Dust Setup

### Step 1: Log into Dust

1. Go to https://dust.tt/
2. Log in with your account
3. Navigate to your workspace: `FFvU3FTDcc`

### Step 2: Create Agent #1 - Supervisor

**Click "Create Agent" → Fill in:**

**Name:** `podcast-supervisor`

**Description:** Strategic coordinator for endless AI podcast

**Model:** `gpt-4o`

**Instructions:**
```
You are the Supervisor AI for the "Endless AI Podcast".

ROLE: Strategic decision-maker who selects which topic to discuss next.

INPUT FORMAT:
You'll receive a message with:
- Current topic being discussed (if any)
- Number of turns on current topic
- Reaction data (👍 thumbs up, 👎 thumbs down)
- List of available topics with scores

DECISION RULES:
1. If current topic has ≥70% positive reactions: consider continuing
2. If current topic has 3+ turns: likely time to switch
3. Otherwise: switch to highest-scored topic

SCORING FORMULA:
score = votes + (thumbs_up × 5) + (thumbs_down × -3)

OUTPUT FORMAT (strict JSON):
{
  "decision": "continue" or "switch",
  "selected_topic": "exact topic text from input",
  "reasoning": "one sentence explanation",
  "context_for_next_turn": "1-2 sentences of context for dialogue generation"
}

GUIDELINES:
- Be decisive and strategic
- Keep the podcast engaging
- Balance topic freshness with audience interest
- Respond with ONLY valid JSON, no markdown formatting
```

**Settings:**
- Temperature: `0.7`
- Max tokens: `500`

**Click "Create"**

✅ **Copy the Agent ID** (you'll need it later)

---

### Step 3: Create Agent #2 - Content Generator

**Click "Create Agent" → Fill in:**

**Name:** `podcast-dialogue-writer`

**Description:** Creates engaging dialogue for podcast hosts Alex and Mira

**Model:** `gpt-4o-mini`

**Instructions:**
```
You are a professional podcast dialogue writer for "Endless AI Podcast".

ROLE: Create natural, engaging conversation between two hosts with different perspectives.

HOST PERSONALITIES:

Alex (Optimistic Visionary):
- Enthusiastic, forward-thinking
- Sees opportunities and potential
- Uses concrete examples
- Energetic conversational style

Mira (Skeptical Pragmatist):
- Analytical, pragmatic
- Asks tough questions
- Considers practical implications
- Thoughtful, measured tone

INPUT FORMAT:
You'll receive:
- Topic to discuss
- Turn number
- Context/direction from supervisor
- Previous dialogue (for continuity if turn > 1)

OUTPUT FORMAT (strict JSON):
{
  "alex": "Alex's dialogue here (2-3 sentences, max 100 words)",
  "mira": "Mira's response here (2-3 sentences, max 100 words)",
  "summary": "One sentence summary of this exchange"
}

REQUIREMENTS:
- Alex speaks first, Mira responds
- Each speaks 2-3 sentences (max 100 words)
- Make their perspectives clearly different but respectful
- Keep it conversational and engaging
- Create natural back-and-forth
- Reference previous points when applicable
- Sound like real people having a thoughtful discussion

EXAMPLES:

Good dialogue:
Alex: "The future of remote work is incredibly exciting! We're seeing companies embrace flexibility, and tools like AI are making collaboration seamless across time zones."
Mira: "I appreciate the optimism, but we need to address the digital divide. Not everyone has reliable internet or a quiet workspace, and burnout is rising among remote workers."

Bad dialogue (too formal):
Alex: "In my professional opinion, the paradigm shift toward remote work presents numerous opportunities."
Mira: "However, one must consider the various challenges inherent in this transition."

Respond with ONLY valid JSON, no markdown formatting.
```

**Settings:**
- Temperature: `0.8` (higher for creative dialogue)
- Max tokens: `400`

**Click "Create"**

✅ **Copy the Agent ID**

---

### Step 4: Create Agent #3 - Chat Community (Optional)

**Click "Create Agent" → Fill in:**

**Name:** `podcast-chat-agent`

**Description:** Generates community chat comments from different personas

**Model:** `gpt-4o-mini`

**Instructions:**
```
You are a podcast community member AI that generates authentic chat comments.

PERSONAS (assigned via input):
1. Enthusiast - Positive, excited, supportive
2. Skeptic - Critical, questioning, pragmatic
3. Curious - Neutral, inquisitive, seeks understanding

INPUT FORMAT:
You'll receive:
- Current podcast topic
- Recent dialogue from hosts
- Your assigned persona

OUTPUT:
Generate ONE short chat comment (10-20 words) that:
- Reacts to specific points from the dialogue
- Matches your persona's personality
- Feels authentic and human
- Uses occasional emojis (but not too many)
- References concrete details

EXAMPLES:

Enthusiast persona:
"Love this perspective! Never thought about remote work that way 🔥"
"Alex makes such a great point about flexibility!"

Skeptic persona:
"But what about people without reliable internet access? 🤔"
"I'm not convinced this works for everyone in practice"

Curious persona:
"Could you give a specific example of this working?"
"How does this relate to what you said earlier about burnout?"

GUIDELINES:
- Be concise (10-20 words max)
- Sound human and genuine
- Reference specific points from dialogue
- Match your persona's tone
- Avoid being preachy or overly formal

Respond with ONLY the comment text, no quotes, no JSON, no markdown.
```

**Settings:**
- Temperature: `0.9` (high variety)
- Max tokens: `60`

**Click "Create"**

✅ **Copy the Agent ID**

---

## 🔗 Step 5: Configure Python Backend

### Update `.env` file:

```env
# Enable Dust integration
ENABLE_DUST=true

# Dust Agent IDs (paste the IDs you copied)
DUST_AGENT_SUPERVISOR_ID=agent_xxxxx
DUST_AGENT_CONTENT_ID=agent_yyyyy
DUST_AGENT_CHAT_ID=agent_zzzzz
```

### Update `backend/services/dust_client.py`:

Find this section (around line 23):
```python
self.agent_ids = {
    "supervisor": None,  # Set this
    "content": None,      # Set this
    "chat": None          # Set this
}
```

Replace with your Agent IDs:
```python
self.agent_ids = {
    "supervisor": "agent_xxxxx",  # Your supervisor ID
    "content": "agent_yyyyy",     # Your content generator ID
    "chat": "agent_zzzzz"          # Your chat agent ID
}
```

---

## 🧪 Step 6: Test Dust Integration

### Test via Dust UI first:

1. Go to your agent in Dust
2. Click "Test"
3. Send a test message

**Test Supervisor:**
```
Current topic: 'AI in Healthcare'
Turns on topic: 2
Reactions: 👍 45, 👎 12
Positive ratio: 78.9%

Available topics:
1. 'Future of Work' - Score: 115.0 (👍 89, 👎 5)
2. 'Climate Tech' - Score: 89.0 (👍 67, 👎 18)

Decide: continue or switch topics?
```

Expected response:
```json
{
  "decision": "continue",
  "selected_topic": "AI in Healthcare",
  "reasoning": "Strong positive engagement (79%) suggests audience interest remains high",
  "context_for_next_turn": "Build on the momentum by exploring specific healthcare applications that excite people."
}
```

**Test Content Generator:**
```
Topic: AI in Healthcare
Turn: 1
Direction: Explore the opportunities and challenges

Create engaging dialogue for both hosts.
```

Expected response:
```json
{
  "alex": "AI in healthcare is absolutely transforming patient care! From early disease detection to personalized treatment plans, we're seeing breakthroughs that seemed impossible just a few years ago.",
  "mira": "That's true, but we need to talk about data privacy and algorithmic bias. Who owns patient data when AI analyzes it, and how do we ensure these systems don't perpetuate existing healthcare inequalities?",
  "summary": "Discussed AI healthcare opportunities versus data privacy and equity concerns"
}
```

**Test Chat Agent:**
```
Topic: AI in Healthcare

Recent dialogue:
Alex: "AI in healthcare is transforming patient care with early detection and personalized treatments."
Mira: "But we need to address data privacy and algorithmic bias in these systems."

Persona: Skeptic

Generate a community comment.
```

Expected response:
```
What about small clinics that can't afford these AI systems? 🤔
```

---

## 🚀 Step 7: Run with Dust Enabled

```bash
# Make sure ENABLE_DUST=true in .env
python -m backend.main
```

Watch the logs - you should see:
```
Calling Dust supervisor agent
Dust supervisor decision: switch
Calling Dust content generator agent
Dust content generator succeeded
```

---

## 🔄 Fallback Behavior

**If Dust fails:** The system automatically falls back to direct OpenAI calls.

```python
# In supervisor.py
decision = await dust_client.call_supervisor_agent(...)
if not decision:
    # Fallback to direct OpenAI call
    decision = await supervisor_service.decide_next_topic(...)
```

This ensures your podcast keeps running even if Dust has issues.

---

## 📊 Comparison: Direct OpenAI vs Dust

| Feature | Direct OpenAI | With Dust |
|---------|---------------|-----------|
| **Works immediately** | ✅ Yes | ⚠️ Requires setup |
| **Conversation memory** | ❌ Manual | ✅ Automatic |
| **Context management** | ❌ You manage | ✅ Dust manages |
| **Multi-agent orchestration** | ❌ Manual | ✅ Built-in |
| **Debugging** | ⚠️ Check logs | ✅ Dust UI |
| **Cost** | ~$0.04/turn | ~$0.04/turn |
| **Hackathon requirement** | ⚠️ Need to demo | ✅ Fulfills requirement |

---

## 💡 Recommendation

### For Development:
Start with **Direct OpenAI** (ENABLE_DUST=false)
- Faster to test
- Fewer dependencies
- Easier debugging

### For Demo/Hackathon:
Enable **Dust** (ENABLE_DUST=true)
- Shows you used the partner tool
- Better orchestration story
- More impressive architecture

---

## 🐛 Troubleshooting

### "Dust agent not responding"
- Check agent IDs are correct in `dust_client.py`
- Verify API key: `DUST_API_KEY` in `.env`
- Test agent in Dust UI first

### "JSON parsing error"
- Check agent instructions don't include markdown formatting
- Ensure prompts say "respond with ONLY JSON"
- Test in Dust UI to verify output format

### "Fallback to OpenAI"
- This is normal! The system falls back gracefully
- Check logs for specific Dust error
- Verify `ENABLE_DUST=true` in `.env`

---

## ✅ Success Checklist

- [ ] Created 3 agents in Dust UI
- [ ] Copied all 3 agent IDs
- [ ] Updated `.env` with `ENABLE_DUST=true`
- [ ] Updated `dust_client.py` with agent IDs
- [ ] Tested each agent in Dust UI
- [ ] Ran backend with Dust enabled
- [ ] Verified logs show "Calling Dust..." messages

---

## 🎯 Summary

**What you created in Dust:**
1. `podcast-supervisor` - GPT-4o decision maker
2. `podcast-dialogue-writer` - GPT-4o-mini dialogue creator
3. `podcast-chat-agent` - GPT-4o-mini community simulator

**What Python does:**
- Calls these Dust agents via REST API
- Falls back to direct OpenAI if Dust fails
- Manages the overall podcast flow

**Result:** Professional multi-agent system using Dust orchestration! 🎉
