import asyncio
import logging
import json
import os

from fastapi import APIRouter, Request

from app.decorators.security import signature_required
from app.services.openai_services import ChatCompletionService
from app.services.whatsapp_services import WhatsAppServices
from pydantic import BaseModel

whatsapp_service = WhatsAppServices(open_ai_chat=ChatCompletionService())

whatsapp_route = APIRouter()
logger = logging.getLogger(__name__)


class Message(BaseModel):
    message: str


@whatsapp_route.get(path="/webhook")
def webhook_get(request: Request):
    return asyncio.run(_verify(request=request))


@whatsapp_route.post(path="/webhook")
@signature_required
def webhook_post(request: Request):
    return asyncio.run(handle_message(request=request))


@whatsapp_route.post(path="/send_message")
def send_message(msg: Message):
    return whatsapp_service.send_message(message=msg.message), 200


async def handle_message(request: Request):
    body = await request.json()
    status_update = (
        body.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("statuses")
    )
    if status_update:
        logger.debug(f"request body: {body}")
        logger.info("Received a WhatsApp status update.")
        return json.dumps({"status": "ok"}), 200

    try:
        if whatsapp_service.is_valid_whatsapp_message(body=body):
            await whatsapp_service.process_whatsapp_message_with_open_ai(body=body)
            return json.dumps({"status": "ok"}), 200
        else:
            return (
                json.dumps({"status": "error", "message": "Not a WhatsApp API event"}),
                404,
            )
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON")
        return json.dumps({"status": "error", "message": "Invalid JSON provided"}), 400


async def _verify(request: Request):
    request = await request.json()
    mode = request.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    # Check if a token and mode were sent
    if mode and token:
        # Check the mode and token sent are correct
        if mode == "subscribe" and token == os.getenv("VERIFY_TOKEN"):
            # Respond with 200 OK and challenge token from the request
            logger.info("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            # Responds with '403 Forbidden' if verify tokens do not match
            logger.info("VERIFICATION_FAILED")
            return json.dumps({"status": "error", "message": "Verification failed"}), 403
    else:
        # Responds with '400 Bad Request' if verify tokens do not match
        logger.info("MISSING_PARAMETER")
        return json.dumps({"status": "error", "message": "Missing parameters"}), 400
