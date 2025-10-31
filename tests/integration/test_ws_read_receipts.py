from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.ai_service.src.api.ws_endpoints import router as ws_router
from backend.ai_service.src.api._dev_endpoints import router as dev_router


def build_test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(ws_router)
    app.include_router(dev_router)
    return app


def test_ws_read_receipts_broadcast():
    app = build_test_app()
    client = TestClient(app)

    with client.websocket_connect("/ws?token=dev1") as ws_a, client.websocket_connect("/ws?token=dev2") as ws_b:
        ws_a.receive_json()  # auth.ok
        ws_b.receive_json()  # auth.ok

        ws_a.send_json({"type": "presence.join", "data": {"cids": ["c-rr"]}})
        ws_b.send_json({"type": "presence.join", "data": {"cids": ["c-rr"]}})
        # Drain join acks
        ws_a.receive_json()
        ws_b.receive_json()

        # Simulate a new message so we have an id to mark read
        r = client.post("/_dev/conversations/c-rr/messages", json={"id": "m-rr-1", "cid": "c-rr"})
        assert r.status_code == 202
        # Drain the broadcast
        for _ in range(3):
            evt = ws_a.receive_json()
            if evt.get("type") == "message.new":
                break

        # Now client B marks as read
        ws_b.send_json({"type": "message.read", "cid": "c-rr", "data": {"mid": "m-rr-1"}})
        # A should receive message.read
        for _ in range(5):
            evt = ws_a.receive_json()
            if evt.get("type") == "message.read":
                assert evt["data"]["mid"] == "m-rr-1"
                assert evt["cid"] == "c-rr"
                break
        else:
            raise AssertionError("message.read not received")


