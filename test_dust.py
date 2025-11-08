"""
Quick test script to verify Dust.tt API connectivity.
"""
import asyncio
import httpx
from backend.config import settings


async def test_dust_connection():
    """Test basic Dust API connection."""
    print("=" * 60)
    print("Testing Dust.tt API Connection")
    print("=" * 60)

    # Check configuration
    print(f"\n✓ Dust API Key: {settings.dust_api_key[:20]}...")
    print(f"✓ Workspace ID: {settings.dust_workspace_id}")
    print(f"✓ Supervisor Agent ID: {settings.dust_agent_supervisor_id}")
    print(f"✓ Content Agent ID: {settings.dust_agent_content_id}")
    print(f"✓ Dust Enabled: {settings.enable_dust}")

    # Test API endpoint
    base_url = "https://dust.tt/api/v1"
    url = f"{base_url}/w/{settings.dust_workspace_id}/assistant/conversations"

    headers = {
        "Authorization": f"Bearer {settings.dust_api_key}",
        "Content-Type": "application/json"
    }

    # Simple test message
    test_message = "Hello! This is a test message from the Unlimited Podcast system. Please respond with 'OK' if you receive this."

    payload = {
        "message": {
            "content": test_message,
            "mentions": [{"configurationId": settings.dust_agent_supervisor_id}],
            "context": {
                "timezone": "America/New_York",
                "username": "test_user",
                "email": None,
                "fullName": None,
                "profilePictureUrl": None
            }
        },
        "blocking": True
    }

    print(f"\n📡 Sending test message to Dust API...")
    print(f"   Endpoint: {url}")
    print(f"   Agent: {settings.dust_agent_supervisor_id}")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)

            print(f"\n✓ Response Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"✓ Response received successfully!")
                print(f"\n📦 Response structure:")
                print(f"   Top-level keys: {list(data.keys())}")

                # Try to extract the response
                response_text = None

                if "conversation" in data:
                    conv = data["conversation"]
                    print(f"   Conversation keys: {list(conv.keys())}")

                    if "content" in conv:
                        content = conv["content"]
                        print(f"   Content type: {type(content)}")
                        if isinstance(content, list):
                            print(f"   Content length: {len(content)}")

                            # Inspect structure
                            for i, item in enumerate(content):
                                print(f"   Content[{i}] type: {type(item)}")
                                if isinstance(item, list) and len(item) > 0:
                                    print(f"      First element: {type(item[0])}")
                                    if isinstance(item[0], dict):
                                        print(f"      Keys: {list(item[0].keys())[:5]}")
                                        if "type" in item[0]:
                                            print(f"      Type: {item[0]['type']}")
                                        # Look for agent messages
                                        for msg in item:
                                            if isinstance(msg, dict) and msg.get("type") == "agent_message":
                                                print(f"      🤖 Found agent message!")
                                                if "content" in msg:
                                                    response_text = msg["content"]
                                                    print(f"      Content preview: {msg['content'][:100]}...")

                if "message" in data:
                    print(f"   Message keys: {list(data['message'].keys()) if isinstance(data['message'], dict) else 'N/A'}")

                if response_text:
                    print(f"\n✅ SUCCESS! Agent responded:")
                    print(f"   {response_text[:200]}...")
                else:
                    print(f"\n⚠️  Could not extract response text from structure")
                    print(f"\n📄 Full response (first 500 chars):")
                    print(f"   {str(data)[:500]}...")

            else:
                print(f"❌ Request failed with status {response.status_code}")
                print(f"   Response: {response.text[:500]}")

    except httpx.HTTPStatusError as e:
        print(f"\n❌ HTTP Error: {e.response.status_code}")
        print(f"   {e.response.text[:500]}")
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(test_dust_connection())
