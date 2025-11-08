"""
Dust API Client for agent orchestration.

This module provides integration with Dust.tt API for multi-agent orchestration.
Falls back to direct OpenAI calls if Dust is not enabled.
"""
from backend.config import settings
from backend.utils.logger import setup_logger
import httpx
from typing import Dict, Optional
import json

logger = setup_logger(__name__)


class DustClient:
    """
    Client for Dust.tt API integration.

    Provides methods to call Dust agents for:
    - Supervisor decisions
    - Content generation
    - Chat agent comments
    """

    def __init__(self):
        """Initialize Dust API client."""
        self.base_url = "https://dust.tt/api/v1"
        self.api_key = settings.dust_api_key
        self.workspace_id = settings.dust_workspace_id
        self.enabled = settings.enable_dust

        # Agent IDs (to be set after creating agents in Dust UI)
        # You'll get these IDs when you create agents in Dust
        self.agent_ids = {
            "supervisor": None,  # Set this after creating "podcast-supervisor" agent
            "content": None,      # Set this after creating "podcast-dialogue-writer" agent
            "chat": None          # Set this after creating "podcast-chat-agent" agent
        }

        self.client = httpx.AsyncClient(timeout=60.0)

    async def call_supervisor_agent(
        self,
        current_topic: Optional[Dict],
        available_topics: list[Dict],
        turns_on_current: int
    ) -> Dict:
        """
        Call Dust supervisor agent for topic selection.

        Args:
            current_topic: Current topic data (or None)
            available_topics: List of available topics with scores
            turns_on_current: Number of turns on current topic

        Returns:
            Decision dictionary from agent
        """
        if not self.enabled or not self.agent_ids["supervisor"]:
            logger.info("Dust supervisor not enabled, using fallback")
            return None  # Will trigger fallback in supervisor.py

        logger.info("Calling Dust supervisor agent")

        # Prepare message for agent
        message = self._format_supervisor_message(
            current_topic, available_topics, turns_on_current
        )

        try:
            # Call Dust API
            response = await self._call_agent(
                agent_id=self.agent_ids["supervisor"],
                message=message
            )

            # Parse response
            decision = json.loads(response)
            logger.info(f"Dust supervisor decision: {decision['decision']}")
            return decision

        except Exception as e:
            logger.error(f"Dust supervisor call failed: {e}", exc_info=True)
            return None  # Trigger fallback

    async def call_content_generator_agent(
        self,
        topic: str,
        context: str,
        turn_number: int,
        last_alex: str = "",
        last_mira: str = ""
    ) -> Dict:
        """
        Call Dust content generator agent for dialogue creation.

        Args:
            topic: Topic to discuss
            context: Context from supervisor
            turn_number: Turn number
            last_alex: Alex's last dialogue
            last_mira: Mira's last dialogue

        Returns:
            Dialogue dictionary with alex, mira, summary
        """
        if not self.enabled or not self.agent_ids["content"]:
            logger.info("Dust content generator not enabled, using fallback")
            return None

        logger.info("Calling Dust content generator agent")

        message = self._format_content_message(
            topic, context, turn_number, last_alex, last_mira
        )

        try:
            response = await self._call_agent(
                agent_id=self.agent_ids["content"],
                message=message
            )

            dialogue = json.loads(response)
            logger.info("Dust content generator succeeded")
            return dialogue

        except Exception as e:
            logger.error(f"Dust content generator failed: {e}", exc_info=True)
            return None

    async def call_chat_agent(
        self,
        topic: str,
        recent_dialogue: str,
        persona: str
    ) -> Optional[str]:
        """
        Call Dust chat agent for community comment.

        Args:
            topic: Current topic
            recent_dialogue: Recent dialogue for context
            persona: Persona to use (Enthusiast/Skeptic/Curious)

        Returns:
            Comment text or None
        """
        if not self.enabled or not self.agent_ids["chat"]:
            return None

        logger.info(f"Calling Dust chat agent ({persona})")

        message = f"""Topic: {topic}

Recent dialogue:
{recent_dialogue}

Persona: {persona}

Generate a community comment."""

        try:
            response = await self._call_agent(
                agent_id=self.agent_ids["chat"],
                message=message
            )

            return response.strip()

        except Exception as e:
            logger.error(f"Dust chat agent failed: {e}", exc_info=True)
            return None

    async def _call_agent(self, agent_id: str, message: str) -> str:
        """
        Generic method to call a Dust agent.

        Args:
            agent_id: Dust agent ID
            message: Message to send to agent

        Returns:
            Agent response text
        """
        url = f"{self.base_url}/w/{self.workspace_id}/assistant/conversations"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "message": {
                "content": message,
                "mentions": [{"configurationId": agent_id}]
            },
            "contentFragment": {
                "title": "Podcast Turn",
                "content": message
            }
        }

        response = await self.client.post(url, headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()

        # Extract agent response from Dust API response
        # (Adjust based on actual Dust API response structure)
        if "message" in data:
            return data["message"]["content"]
        elif "content" in data:
            return data["content"]
        else:
            raise ValueError(f"Unexpected Dust API response: {data}")

    def _format_supervisor_message(
        self,
        current_topic: Optional[Dict],
        available_topics: list[Dict],
        turns_on_current: int
    ) -> str:
        """Format message for supervisor agent."""
        msg = "**Supervisor Decision Request**\n\n"

        if current_topic:
            msg += f"Current topic: '{current_topic['text']}'\n"
            msg += f"Turns on topic: {turns_on_current}\n"
            msg += f"Reactions: 👍 {current_topic.get('thumbs_up', 0)}, 👎 {current_topic.get('thumbs_down', 0)}\n"
            msg += f"Positive ratio: {current_topic.get('positive_ratio', 0):.1%}\n\n"
        else:
            msg += "No current topic (first turn)\n\n"

        msg += "Available topics:\n"
        for i, topic in enumerate(available_topics[:5], 1):
            msg += f"{i}. '{topic['text']}' - Score: {topic.get('score', 0):.1f} "
            msg += f"(👍 {topic.get('thumbs_up', 0)}, 👎 {topic.get('thumbs_down', 0)})\n"

        msg += "\nDecide: continue or switch topics?"

        return msg

    def _format_content_message(
        self,
        topic: str,
        context: str,
        turn_number: int,
        last_alex: str,
        last_mira: str
    ) -> str:
        """Format message for content generator agent."""
        msg = f"**Generate Podcast Dialogue**\n\n"
        msg += f"Topic: {topic}\n"
        msg += f"Turn: {turn_number}\n"
        msg += f"Direction: {context}\n\n"

        if turn_number > 1 and (last_alex or last_mira):
            msg += "Previous turn:\n"
            if last_alex:
                msg += f"Alex: {last_alex}\n"
            if last_mira:
                msg += f"Mira: {last_mira}\n"
            msg += "\n"

        msg += "Create engaging dialogue for both hosts."

        return msg

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global Dust client instance
dust_client = DustClient()
