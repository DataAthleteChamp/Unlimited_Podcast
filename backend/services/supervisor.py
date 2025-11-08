"""
Supervisor LLM Service - The "Referee Brain"

This service uses GPT-4o to make strategic decisions about:
- Which topic to discuss next
- Whether to continue current topic or switch
- Context management for the podcast
"""
from openai import AsyncOpenAI
from backend.config import settings
from backend.models import Topic
from backend.utils.logger import setup_logger
from typing import Dict, List, Optional
import json

logger = setup_logger(__name__)


class SupervisorService:
    """
    Supervisor AI that coordinates the podcast flow.

    Uses GPT-4o for strategic decision-making.
    """

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.supervisor_model

    async def decide_next_topic(
        self,
        current_topic: Optional[Topic],
        available_topics: List[Topic],
        turns_on_current: int
    ) -> Dict:
        """
        Decide whether to continue current topic or switch to new one.

        Args:
            current_topic: Currently discussed topic (if any)
            available_topics: List of available topics with scores
            turns_on_current: Number of turns spent on current topic

        Returns:
            Dictionary with decision details:
            {
                "decision": "continue" | "switch",
                "selected_topic": Topic object,
                "reasoning": str,
                "context_for_next_turn": str
            }
        """
        logger.info(f"Supervisor deciding next topic. Current: {current_topic.text if current_topic else 'None'}")

        # Prepare topic data for the prompt
        topics_data = [
            {
                "text": topic.text,
                "votes": topic.votes,
                "thumbs_up": topic.reactions_thumbs_up,
                "thumbs_down": topic.reactions_thumbs_down,
                "score": topic.score,
                "positive_ratio": topic.positive_ratio
            }
            for topic in available_topics[:5]  # Top 5 topics
        ]

        current_topic_data = None
        if current_topic:
            current_topic_data = {
                "text": current_topic.text,
                "turns": turns_on_current,
                "thumbs_up": current_topic.reactions_thumbs_up,
                "thumbs_down": current_topic.reactions_thumbs_down,
                "positive_ratio": current_topic.positive_ratio
            }

        # Construct prompt
        prompt = self._build_decision_prompt(current_topic_data, topics_data)

        try:
            # Call GPT-4o
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are the Supervisor AI for an endless podcast. "
                                   "Make strategic decisions about topic selection. "
                                   "Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )

            # Parse response
            decision_text = response.choices[0].message.content.strip()
            logger.debug(f"Supervisor raw response: {decision_text}")

            # Extract JSON from response (might be wrapped in markdown)
            if "```json" in decision_text:
                decision_text = decision_text.split("```json")[1].split("```")[0].strip()
            elif "```" in decision_text:
                decision_text = decision_text.split("```")[1].split("```")[0].strip()

            decision = json.loads(decision_text)

            # Validate and attach selected topic object
            if decision["decision"] == "continue" and current_topic:
                decision["selected_topic"] = current_topic
            else:
                # Find the topic by text
                selected_text = decision.get("selected_topic", "")
                selected_topic = next(
                    (t for t in available_topics if t.text == selected_text),
                    available_topics[0] if available_topics else None
                )
                decision["selected_topic"] = selected_topic

            logger.info(f"Supervisor decision: {decision['decision']} - {decision['selected_topic'].text if decision['selected_topic'] else 'None'}")

            return decision

        except Exception as e:
            logger.error(f"Supervisor decision failed: {e}", exc_info=True)

            # Fallback: Select top-scored topic
            top_topic = available_topics[0] if available_topics else current_topic

            return {
                "decision": "switch" if top_topic != current_topic else "continue",
                "selected_topic": top_topic,
                "reasoning": "Fallback to highest-scored topic due to AI error",
                "context_for_next_turn": "Starting fresh discussion."
            }

    def _build_decision_prompt(
        self,
        current_topic: Optional[Dict],
        available_topics: List[Dict]
    ) -> str:
        """Build the decision prompt for the supervisor."""

        prompt = """You are the Supervisor AI referee for an endless podcast.

**Current State:**
"""
        if current_topic:
            prompt += f"""
- Current topic: "{current_topic['text']}"
- Turns on this topic: {current_topic['turns']}
- Reactions: 👍 {current_topic['thumbs_up']}, 👎 {current_topic['thumbs_down']}
- Positive ratio: {current_topic['positive_ratio']:.1%}
"""
        else:
            prompt += "\n- No current topic (first turn)\n"

        prompt += f"""
**Available Topics (sorted by score):**
"""
        for i, topic in enumerate(available_topics, 1):
            prompt += f"""
{i}. "{topic['text']}"
   - Votes: {topic['votes']}
   - Reactions: 👍 {topic['thumbs_up']}, 👎 {topic['thumbs_down']}
   - Score: {topic['score']:.1f}
   - Positive ratio: {topic['positive_ratio']:.1%}
"""

        prompt += f"""
**Decision Rules:**
1. If current topic has positive ratio ≥ {settings.topic_continuation_threshold:.0%}: Consider continuing
2. If current topic has been discussed for 3+ turns: Likely time to switch
3. Otherwise: Switch to highest-scored topic

**Your Task:**
Decide whether to CONTINUE the current topic or SWITCH to a new one.

**Output Format (JSON only):**
```json
{{
  "decision": "continue" or "switch",
  "selected_topic": "exact topic text",
  "reasoning": "brief explanation (1 sentence)",
  "context_for_next_turn": "context for content generator (1-2 sentences)"
}}
```

Respond with ONLY the JSON, no additional text.
"""
        return prompt


# Global supervisor instance
supervisor_service = SupervisorService()
