import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.orm import Session

@pytest.mark.asyncio
async def test_multi_device_sync_flow(client: AsyncClient, db_session: Session, authenticated_user_headers: dict):
    """
    Integration test for multi-device data synchronization.
    1. User starts a conversation on Device A.
    2. The new conversation and messages are created.
    3. User logs in on Device B.
    4. Device B can fetch the latest conversation history.
    5. User sends a message from Device B.
    6. Device A receives the update (simulated via polling/websocket).
    """
    # This test is complex as it simulates two clients.
    # We will use the same client but check for state consistency.
    
    # Pre-requisite: An AI companion exists.
    companion_id = "some_companion_id"

    # Step 1 & 2: Start conversation on "Device A"
    conv_payload = {"ai_companion_id": companion_id, "title": "Sync Test"}
    conv_response = await client.post("/conversations", json=conv_payload, headers=authenticated_user_headers)
    assert conv_response.status_code == 201
    conversation_id = conv_response.json()["id"]

    msg_payload_A = {"content": "Message from Device A"}
    await client.post(f"/conversations/{conversation_id}/messages", json=msg_payload_A, headers=authenticated_user_headers)

    # Step 3 & 4: "Device B" fetches the history
    await asyncio.sleep(1) # Simulate delay
    history_response_B = await client.get(f"/conversations/{conversation_id}/messages", headers=authenticated_user_headers)
    assert history_response_B.status_code == 200
    messages_B = history_response_B.json()["messages"]
    assert len(messages_B) > 0
    assert messages_B[-1]["content"] == "Message from Device A"

    # Step 5: "Device B" sends a message
    msg_payload_B = {"content": "Reply from Device B"}
    await client.post(f"/conversations/{conversation_id}/messages", json=msg_payload_B, headers=authenticated_user_headers)

    # Step 6: "Device A" polls for updates
    await asyncio.sleep(1)
    history_response_A_updated = await client.get(f"/conversations/{conversation_id}/messages", headers=authenticated_user_headers)
    assert history_response_A_updated.status_code == 200
    messages_A_updated = history_response_A_updated.json()["messages"]
    assert messages_A_updated[-1]["content"] == "Reply from Device B"
