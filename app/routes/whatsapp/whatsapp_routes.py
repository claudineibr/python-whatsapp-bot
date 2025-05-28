import asyncio
import logging
import json
import os

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, PlainTextResponse

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
async def webhook_post(request: Request):
    return await handle_message(request=request)


@whatsapp_route.post(path="/send_message")
async def send_message(msg: Message):
    return await whatsapp_service.send_message(message=msg.message), 200


async def handle_message(request: Request):
    body = await request.json()
    status_update = (
        body.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("statuses")
    )
    if status_update:
        logger.debug(f"Received a WhatsApp status update.: {body}")
        await whatsapp_service.update_status(body=status_update)
        return JSONResponse(content={"status": "ok"}, status_code=200)

    try:
        if whatsapp_service.is_valid_whatsapp_message(body=body):
            await whatsapp_service.create_message(body=body)
            # await whatsapp_service.process_whatsapp_message_with_open_ai(body=body)
            return JSONResponse(content={"status": "ok"}, status_code=200)
        else:
            return JSONResponse(content={"status": "error", "message": "Not a WhatsApp API event"}, status_code=404)
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON")
        return JSONResponse(content={"status": "error", "message": "Invalid JSON provided"}, status_code=400)


async def _verify(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == os.getenv("VERIFY_TOKEN"):
            logger.info("WEBHOOK_VERIFIED")
            return PlainTextResponse(content=challenge, status_code=200)
        else:
            logger.info("VERIFICATION_FAILED")
            return JSONResponse(content={"status": "error", "message": "Verification failed"}, status_code=403)
    else:
        logger.info("MISSING_PARAMETER")
        return JSONResponse(content={"status": "error", "message": "Missing parameters"}, status_code=400)
