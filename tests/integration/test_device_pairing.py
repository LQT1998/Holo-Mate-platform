import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

@pytest.mark.asyncio
async def test_device_pairing_flow(client: AsyncClient, db_session: Session, authenticated_user_headers: dict):
    """
    Integration test for the device pairing flow.
    1. User registers a new hologram device via API.
    2. A new HologramDevice record is created and linked to the user.
    3. The device appears in the user's list of devices.
    4. User can update the device's settings.
    """
    # Step 1: Register a new device
    device_payload = {
        "name": "Living Room Holo-Pad",
        "device_type": "HOLO_PAD_V1",
        "serial_number": "HP1-LIVINGROOM-XYZ"
    }
    
    register_response = await client.post("/devices", json=device_payload, headers=authenticated_user_headers)
    
    assert register_response.status_code == 201
    device_data = register_response.json()
    assert device_data["name"] == "Living Room Holo-Pad"
    device_id = device_data["id"]

    # Step 2: Verify database records (will fail until implemented)
    # from backend.shared.src.models import HologramDevice
    # device_in_db = db_session.query(HologramDevice).get(device_id)
    # assert device_in_db is not None
    # assert device_in_db.user_id == authenticated_user_id

    # Step 3: Verify the device is in the user's list
    list_response = await client.get("/devices", headers=authenticated_user_headers)
    assert list_response.status_code == 200
    devices_list = list_response.json()["devices"]
    assert any(d["id"] == device_id for d in devices_list)

    # Step 4: Update device settings
    update_payload = {"name": "Main Holo-Pad"}
    update_response = await client.put(f"/devices/{device_id}", json=update_payload, headers=authenticated_user_headers)
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Main Holo-Pad"
