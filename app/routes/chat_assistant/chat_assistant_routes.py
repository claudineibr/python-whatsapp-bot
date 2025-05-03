import logging
import asyncio

from flask import (
    Blueprint,
    request,
)

from app.services.openai_services import ChatAssistantService

logger = logging.getLogger(__name__)

chat_assistant_service = ChatAssistantService()
chat_assistant_blueprint = Blueprint("chat_assistant", import_name=__name__, url_prefix="/openai")

@chat_assistant_blueprint.route("/chat_assistant/send_message", methods=["POST"])
def send_message():

    message_body = request.json.get("message")
    key = request.json.get("key")
    data = {"key": key, "message": message_body}
    return chat_assistant_service.generate_response(data=data), 200

