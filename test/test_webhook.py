from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.routes.whatsapp.whatsapp_routes import whatsapp_route

app = FastAPI()
app.include_router(whatsapp_route)

client = TestClient(app)

def test_status_update_event():
    payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "statuses": [{"status": "delivered"}]
                }
            }]
        }]
    }

    response = client.post("/webhook", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_valid_message_event(monkeypatch):
    payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{"text": {"body": "hello"}}]
                }
            }]
        }]
    }

    async def mock_process(body):
        return

    monkeypatch.setattr(
        "app.webhook.whatsapp_service.process_whatsapp_message_with_open_ai",
        mock_process
    )

    response = client.post("/webhook", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_invalid_event():
    payload = {"some": "unknown format"}

    response = client.post("/webhook", json=payload)
    assert response.status_code == 404
    assert response.json() == {"status": "error", "message": "Not a WhatsApp API event"}
