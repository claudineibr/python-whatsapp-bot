import asyncio
import logging
import json

from flask import (
    Blueprint,
    request,
    jsonify,
    current_app,
)

from app.decorators.security import signature_required
from app.services.openai_services import ChatCompletionService
from app.services.whatsapp_services import WhatsAppServices

whatsapp_service = WhatsAppServices(open_ai_chat=ChatCompletionService())

whatsapp_blueprint = Blueprint("whatsapp", __name__)
logger = logging.getLogger(__name__)

@whatsapp_blueprint.route("/webhook", methods=["GET"])
def webhook_get():
    return _verify()

@whatsapp_blueprint.route("/webhook", methods=["POST"])
@signature_required
def webhook_post():
    return asyncio.run(handle_message())

@whatsapp_blueprint.route("/send_message", methods=["POS"])
def send_message():
    message = request.json.get("message")
    return whatsapp_service.send_message(message=message), 200


async def handle_message():
    body = request.get_json()
    status_update = (
        body.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("statuses")
    )
    if status_update:
        logging.debug(f"request body: {body}")
        logging.info("Received a WhatsApp status update.")
        return jsonify({"status": "ok"}), 200

    try:
        if whatsapp_service.is_valid_whatsapp_message(body=body):
            await whatsapp_service.process_whatsapp_message_with_open_ai(body)
            return jsonify({"status": "ok"}), 200
        else:
            return (
                jsonify({"status": "error", "message": "Not a WhatsApp API event"}),
                404,
            )
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON")
        return jsonify({"status": "error", "message": "Invalid JSON provided"}), 400

def _verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    # Check if a token and mode were sent
    if mode and token:
        # Check the mode and token sent are correct
        if mode == "subscribe" and token == current_app.config["VERIFY_TOKEN"]:
            # Respond with 200 OK and challenge token from the request
            logging.info("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            # Responds with '403 Forbidden' if verify tokens do not match
            logging.info("VERIFICATION_FAILED")
            return jsonify({"status": "error", "message": "Verification failed"}), 403
    else:
        # Responds with '400 Bad Request' if verify tokens do not match
        logging.info("MISSING_PARAMETER")
        return jsonify({"status": "error", "message": "Missing parameters"}), 400
