"""
Chat Agent Service - AI Personas for Community Simulation

Creates AI-generated chat comments from 3 different personas to simulate
community engagement and create a lively atmosphere.
"""
from openai import AsyncOpenAI
from backend.config import settings
from backend.models import ChatMessage, ChatAgentPersona
from backend.utils.logger import setup_logger
from typing import List
import random

logger = setup_logger(__name__)


# Define the 3 AI chat personas
CHAT_PERSONAS: List[ChatAgentPersona] = [
    ChatAgentPersona(
        name="AI_Enthusiast",
        personality="Positive, excited, supportive",
        emoji="✨",
        system_prompt="""You are an enthusiastic podcast community member.
You're positive, excited about new ideas, and supportive of the hosts.
Generate SHORT chat comments (10-20 words) that:
- Show genuine enthusiasm
- Reference specific points from the dialogue
- Ask curious questions
- Use occasional emojis (but not too many)
- Feel authentic and human

Examples:
- "Love this perspective! Never thought about it that way 🔥"
- "Alex makes a great point about the opportunities here"
- "Can you expand on that idea about automation?"
"""
    ),
    ChatAgentPersona(
        name="AI_Skeptic",
        personality="Critical, questioning, pragmatic",
        emoji="🤔",
        system_prompt="""You are a skeptical podcast community member.
You ask tough questions, point out challenges, and keep discussions grounded.
Generate SHORT chat comments (10-20 words) that:
- Question assumptions
- Point out practical concerns
- Play devil's advocate
- Remain respectful but critical
- Feel authentic and thoughtful

Examples:
- "But what about the people who lose their jobs in this scenario?"
- "I'm not convinced this would actually work in practice 🤔"
- "Interesting, but the data doesn't really support that claim"
"""
    ),
    ChatAgentPersona(
        name="AI_Curious",
        personality="Neutral, inquisitive, seeks understanding",
        emoji="💭",
        system_prompt="""You are a curious podcast community member.
You ask clarifying questions, seek deeper understanding, and connect ideas.
Generate SHORT chat comments (10-20 words) that:
- Ask for clarification
- Connect to related topics
- Seek examples
- Remain neutral and open-minded
- Feel authentic and engaged

Examples:
- "Could you give a specific example of this in action?"
- "How does this relate to what we discussed earlier about privacy?"
- "Interesting! What's the timeline on something like this?"
"""
    )
]


class ChatAgentService:
    """
    Service for generating AI chat comments from different personas.

    Uses GPT-4o-mini to create contextual, diverse community engagement.
    """

    def __init__(self):
        """Initialize OpenAI client and personas."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.chat_agent_model
        self.personas = CHAT_PERSONAS

    async def generate_comment(
        self,
        current_topic: str,
        recent_dialogue: str,
        persona_name: str = None
    ) -> ChatMessage:
        """
        Generate a chat comment from an AI persona.

        Args:
            current_topic: Current podcast topic
            recent_dialogue: Recent dialogue text for context
            persona_name: Specific persona to use (random if None)

        Returns:
            ChatMessage with AI-generated comment
        """
        # Select persona
        if persona_name:
            persona = next((p for p in self.personas if p.name == persona_name), self.personas[0])
        else:
            persona = random.choice(self.personas)

        logger.info(f"Generating comment from {persona.name}")

        prompt = f"""Current podcast topic: "{current_topic}"

Recent dialogue:
{recent_dialogue}

Generate a SHORT chat comment (10-20 words) that reacts to what was just said.
Be authentic, conversational, and reference specific points.

Respond with ONLY the comment text, nothing else.
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": persona.system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.9,  # High creativity for variety
                max_tokens=60
            )

            comment_text = response.choices[0].message.content.strip()

            # Remove quotes if present
            comment_text = comment_text.strip('"').strip("'")

            logger.info(f"{persona.name} generated: {comment_text}")

            # Create chat message
            chat_message = ChatMessage(
                nickname=persona.name,
                message=comment_text,
                is_ai=True,
                persona=persona.personality
            )

            return chat_message

        except Exception as e:
            logger.error(f"Failed to generate comment from {persona.name}: {e}", exc_info=True)

            # Fallback comment
            fallback_comments = [
                "Interesting discussion! 👀",
                "Great points from both sides",
                "This is a complex topic for sure 🤔",
                "Love where this conversation is going!"
            ]

            return ChatMessage(
                nickname=persona.name,
                message=random.choice(fallback_comments),
                is_ai=True,
                persona=persona.personality
            )

    async def generate_multiple_comments(
        self,
        current_topic: str,
        recent_dialogue: str,
        count: int = 2
    ) -> List[ChatMessage]:
        """
        Generate multiple comments from different personas.

        Args:
            current_topic: Current podcast topic
            recent_dialogue: Recent dialogue for context
            count: Number of comments to generate

        Returns:
            List of ChatMessage objects
        """
        # Shuffle personas for variety
        personas_to_use = random.sample(self.personas, min(count, len(self.personas)))

        comments = []
        for persona in personas_to_use:
            comment = await self.generate_comment(
                current_topic=current_topic,
                recent_dialogue=recent_dialogue,
                persona_name=persona.name
            )
            comments.append(comment)

        return comments


# Global chat agent service instance
chat_agent_service = ChatAgentService()
