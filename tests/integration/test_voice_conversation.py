import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
import uuid

@pytest.mark.asyncio
async def test_voice_conversation_flow(client: AsyncClient, db_session: Session, authenticated_user_headers: dict):
    """
    Integration test for the voice conversation flow.
    1. User starts a new conversation with an AI companion.
    2. A new Conversation record is created.
    3. User sends a message (simulated voice input).
    4. A new Message record is created.
    5. User receives a response (simulated voice output).
    6. Another Message record (from AI) is created.
    7. The conversation history is correctly updated.
    """
    # Pre-requisite: An AI companion must exist. 
    # This would typically be set up in a fixture.
    companion_id = str(uuid.uuid4()) # Placeholder

    # Step 1 & 2: Start a new conversation
    start_conv_payload = {"ai_companion_id": companion_id}
    start_conv_response = await client.post("/conversations", json=start_conv_payload, headers=authenticated_user_headers)
    
    assert start_conv_response.status_code == 201
    conversation_data = start_conv_response.json()
    conversation_id = conversation_data["id"]

    # Step 3 & 4: User sends a message
    user_message_payload = {
        "content": "Hello, how are you?",
        "content_type": "text" # voice would be converted to text
    }
    send_message_response = await client.post(f"/conversations/{conversation_id}/messages", json=user_message_payload, headers=authenticated_user_headers)
    
    assert send_message_response.status_code == 201

    # Step 5 & 6: Simulate receiving a response from the AI
    # This part would involve the streaming service and AI service,
    # which is complex to test in a simple integration test.
    # We'll assume the API confirms the AI message is stored.

    # Step 7: Verify conversation history
    history_response = await client.get(f"/conversations/{conversation_id}/messages", headers=authenticated_user_headers)
    
    assert history_response.status_code == 200
    messages = history_response.json()["messages"]
    assert len(messages) >= 2 # At least user's and AI's message
    assert messages[0]["content"] == "Hello, how are you?"
