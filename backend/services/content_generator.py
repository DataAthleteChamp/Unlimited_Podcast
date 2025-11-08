"""
Content Generator LLM Service - The "Dialogue Writer"

This service uses GPT-4o-mini to generate podcast dialogue for both speakers.
One LLM writes the entire conversation like a screenplay.
"""
from openai import AsyncOpenAI
from backend.config import settings
from backend.utils.logger import setup_logger
from typing import Dict
import json

logger = setup_logger(__name__)


# Persona definitions
PERSONAS = {
    "Alex": {
        "name": "Alex",
        "role": "Optimistic Visionary",
        "traits": "enthusiastic, forward-thinking, sees opportunities",
        "style": "energetic, conversational, uses examples",
        "system_prompt": """You are Alex, an enthusiastic and optimistic podcast host.
You see potential and possibilities in every topic. You're forward-thinking and highlight opportunities.
Speak conversationally in 2-3 sentences (max 100 words). Be engaging and inspiring."""
    },
    "Mira": {
        "name": "Mira",
        "role": "Skeptical Pragmatist",
        "traits": "analytical, pragmatic, asks tough questions",
        "style": "thoughtful, measured, considers challenges",
        "system_prompt": """You are Mira, a thoughtful and pragmatic podcast host.
You ask tough questions and consider practical implications. You're analytical but friendly.
Speak conversationally in 2-3 sentences (max 100 words). Balance skepticism with constructiveness."""
    }
}


class ContentGeneratorService:
    """
    Content Generator AI that creates podcast dialogue.

    Uses GPT-4o-mini to write conversational dialogue for both speakers.
    """

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.content_model

    async def generate_dialogue(
        self,
        topic: str,
        context: str,
        turn_number: int,
        last_alex_text: str = "",
        last_mira_text: str = ""
    ) -> Dict[str, str]:
        """
        Generate dialogue for both Alex and Mira.

        Args:
            topic: Topic being discussed
            context: Context from supervisor (what angle to take)
            turn_number: Turn number in sequence
            last_alex_text: Alex's last dialogue (for continuity)
            last_mira_text: Mira's last dialogue (for continuity)

        Returns:
            Dictionary with:
            {
                "alex": str,
                "mira": str,
                "summary": str
            }
        """
        logger.info(f"Generating dialogue for topic: {topic}, turn: {turn_number}")

        prompt = self._build_dialogue_prompt(
            topic, context, turn_number, last_alex_text, last_mira_text
        )

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a skilled podcast dialogue writer. "
                                   "Create natural, engaging conversations between two hosts with different perspectives. "
                                   "Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,  # Higher creativity for dialogue
                max_tokens=400
            )

            # Parse response
            dialogue_text = response.choices[0].message.content.strip()
            logger.debug(f"Content generator raw response: {dialogue_text}")

            # Extract JSON
            if "```json" in dialogue_text:
                dialogue_text = dialogue_text.split("```json")[1].split("```")[0].strip()
            elif "```" in dialogue_text:
                dialogue_text = dialogue_text.split("```")[1].split("```")[0].strip()

            dialogue = json.loads(dialogue_text)

            logger.info(f"Generated dialogue successfully. Alex: {len(dialogue['alex'])} chars, Mira: {len(dialogue['mira'])} chars")

            return dialogue

        except Exception as e:
            logger.error(f"Content generation failed: {e}", exc_info=True)

            # Fallback dialogue
            return {
                "alex": f"Let's explore {topic}. This is a fascinating area with lots of potential!",
                "mira": f"That's interesting, Alex. But we should also consider the practical challenges involved.",
                "summary": f"Discussed {topic} from optimistic and pragmatic angles."
            }

    def _build_dialogue_prompt(
        self,
        topic: str,
        context: str,
        turn_number: int,
        last_alex: str,
        last_mira: str
    ) -> str:
        """Build the dialogue generation prompt."""

        prompt = f"""Generate a podcast dialogue segment.

**Topic:** {topic}

**Context/Direction:** {context}

**Turn Number:** {turn_number}

"""
        if turn_number > 1 and (last_alex or last_mira):
            prompt += f"""**Previous Turn (for continuity):**
- Alex said: "{last_alex}"
- Mira said: "{last_mira}"

"""

        prompt += f"""**Speakers:**

1. **Alex** ({PERSONAS['Alex']['role']})
   - Personality: {PERSONAS['Alex']['traits']}
   - Style: {PERSONAS['Alex']['style']}

2. **Mira** ({PERSONAS['Mira']['role']})
   - Personality: {PERSONAS['Mira']['traits']}
   - Style: {PERSONAS['Mira']['style']}

**Requirements:**
- Alex speaks first (2-3 sentences, max 100 words)
- Mira responds (2-3 sentences, max 100 words)
- Create natural back-and-forth conversation
- Alex is optimistic and sees opportunities
- Mira is pragmatic and asks tough questions
- Keep it engaging and conversational
- Make their perspectives clearly different but respectful

**Output Format (JSON only):**
```json
{{
  "alex": "Alex's dialogue here (2-3 sentences)",
  "mira": "Mira's response here (2-3 sentences)",
  "summary": "One sentence summary of this exchange"
}}
```

Respond with ONLY the JSON, no additional text.
"""
        return prompt


# Global content generator instance
content_generator_service = ContentGeneratorService()
