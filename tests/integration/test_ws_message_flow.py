from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.ai_service.src.api.ws_endpoints import router as ws_router
from backend.ai_service.src.api._dev_endpoints import router as dev_router


def build_test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(ws_router)
    app.include_router(dev_router)
    return app


def test_ws_message_flow_broadcast():
    app = build_test_app()
    client = TestClient(app)

    with client.websocket_connect("/ws?token=dev1") as ws_a, client.websocket_connect("/ws?token=dev2") as ws_b:
        assert ws_a.receive_json()["type"] in ("auth.ok",)
        assert ws_b.receive_json()["type"] in ("auth.ok",)

        ws_a.send_json({"type": "presence.join", "data": {"cids": ["c-xyz"]}})
        ws_b.send_json({"type": "presence.join", "data": {"cids": ["c-xyz"]}})
        assert ws_a.receive_json()["type"] == "presence.join"
        assert ws_b.receive_json()["type"] == "presence.join"

        r = client.post("/_dev/conversations/c-xyz/messages", json={"id": "m1", "text": "hello"})
        assert r.status_code == 202

        # Drain until we see message.new (ignore presence/heartbeat ordering)
        for _ in range(5):
            evt = ws_a.receive_json()
            if evt.get("type") == "message.new":
                assert evt["data"]["text"] == "hello"
                break
        else:
            raise AssertionError("message.new not received")


