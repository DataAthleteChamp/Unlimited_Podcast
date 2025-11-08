"""
Comprehensive test of Dust.tt integration with actual client code.
"""
import asyncio
import logging
from backend.services.dust_client import dust_client
from backend.config import settings

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')


async def test_supervisor_agent():
    """Test the supervisor agent."""
    print("\n" + "=" * 60)
    print("Testing Supervisor Agent")
    print("=" * 60)

    # Sample data for supervisor
    current_topic = {
        "text": "Artificial Intelligence in Healthcare",
        "turns": 2,
        "thumbs_up": 15,
        "thumbs_down": 3,
        "positive_ratio": 0.83,
        "score": 42.5
    }

    available_topics = [
        {
            "text": "Climate Change Solutions",
            "votes": 10,
            "thumbs_up": 20,
            "thumbs_down": 2,
            "score": 55.0,
            "positive_ratio": 0.91
        },
        {
            "text": "Space Exploration Updates",
            "votes": 8,
            "thumbs_up": 12,
            "thumbs_down": 5,
            "score": 38.0,
            "positive_ratio": 0.71
        }
    ]

    try:
        print(f"✓ Calling supervisor agent: {settings.dust_agent_supervisor_id}")

        result = await dust_client.call_supervisor_agent(
            current_topic=current_topic,
            available_topics=available_topics,
            turns_on_current=2
        )

        if result:
            print(f"✅ SUCCESS! Supervisor responded:")
            print(f"   Decision: {result.get('decision', 'N/A')}")
            print(f"   Selected Topic: {result.get('selected_topic', 'N/A')}")
            print(f"   Reasoning: {result.get('reasoning', 'N/A')}")
            print(f"   Context: {result.get('context_for_next_turn', 'N/A')[:100]}...")
            return True
        else:
            print(f"⚠️  Supervisor returned None (would fall back to OpenAI)")
            return False

    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return False


async def test_content_generator_agent():
    """Test the content generator agent."""
    print("\n" + "=" * 60)
    print("Testing Content Generator Agent")
    print("=" * 60)

    try:
        print(f"✓ Calling content generator agent: {settings.dust_agent_content_id}")

        result = await dust_client.call_content_generator_agent(
            topic="The Future of Renewable Energy",
            context="Introduce the topic with optimism and practical considerations",
            turn_number=1,
            last_alex="",
            last_mira=""
        )

        if result:
            print(f"✅ SUCCESS! Content generator responded:")
            print(f"   Alex: {result.get('alex', 'N/A')[:150]}...")
            print(f"   Mira: {result.get('mira', 'N/A')[:150]}...")
            print(f"   Summary: {result.get('summary', 'N/A')}")
            return True
        else:
            print(f"⚠️  Content generator returned None (would fall back to OpenAI)")
            return False

    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Dust.tt Integration Test")
    print("=" * 60)

    print(f"\n📋 Configuration:")
    print(f"   Dust Enabled: {settings.enable_dust}")
    print(f"   API Key: {settings.dust_api_key[:20]}...")
    print(f"   Workspace ID: {settings.dust_workspace_id}")
    print(f"   Supervisor Agent: {settings.dust_agent_supervisor_id}")
    print(f"   Content Agent: {settings.dust_agent_content_id}")

    if not settings.enable_dust:
        print("\n⚠️  WARNING: ENABLE_DUST is set to False in .env")
        print("   The dust_client will return None and fall back to OpenAI")
        print("   Set ENABLE_DUST=true to test Dust agents\n")

    # Run tests
    supervisor_ok = await test_supervisor_agent()
    content_ok = await test_content_generator_agent()

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Supervisor Agent: {'✅ PASS' if supervisor_ok else '❌ FAIL'}")
    print(f"Content Generator: {'✅ PASS' if content_ok else '❌ FAIL'}")

    if supervisor_ok and content_ok:
        print(f"\n🎉 All tests passed! Dust integration is working perfectly.")
    elif not settings.enable_dust:
        print(f"\n⚠️  Tests show fallback behavior (ENABLE_DUST=false)")
    else:
        print(f"\n⚠️  Some tests failed. Check the errors above.")

    print("=" * 60)

    # Cleanup
    await dust_client.close()


if __name__ == "__main__":
    asyncio.run(main())
