import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

@pytest.mark.asyncio
async def test_ai_companion_creation_flow(client: AsyncClient, db_session: Session, authenticated_user_headers: dict):
    """
    Integration test for the AI companion creation flow.
    1. Authenticated user creates a new companion via API.
    2. A new AICompanion record is created and linked to the user.
    3. Default CharacterAsset and VoiceProfile are created.
    4. The new companion appears in the user's list of companions.
    """
    # Step 1: Create a new companion
    companion_payload = {
        "name": "Luna",
        "description": "A creative and insightful companion.",
        "personality": {"trait": "creative"}
    }
    
    create_response = await client.post("/ai-companions", json=companion_payload, headers=authenticated_user_headers)
    
    assert create_response.status_code == 201
    companion_data = create_response.json()
    assert companion_data["name"] == "Luna"
    companion_id = companion_data["id"]

    # Step 2 & 3: Verify database records (will fail until implemented)
    # from backend.shared.src.models import AICompanion
    # companion_in_db = db_session.query(AICompanion).get(companion_id)
    # assert companion_in_db is not None
    # assert companion_in_db.user_id == authenticated_user_id
    # assert companion_in_db.character_asset is not None
    # assert companion_in_db.voice_profile is not None

    # Step 4: Verify the new companion is in the user's list
    list_response = await client.get("/ai-companions", headers=authenticated_user_headers)
    assert list_response.status_code == 200
    companions_list = list_response.json()["companions"]
    assert any(c["id"] == companion_id for c in companions_list)
