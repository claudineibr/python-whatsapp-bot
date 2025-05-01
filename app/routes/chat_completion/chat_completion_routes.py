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

logger = logging.getLogger(__name__)

chat_completion_service = ChatCompletionService()
chat_completion_blueprint = Blueprint("chat_completion", __name__)

@chat_completion_blueprint.route("/chat_completion/send_message", methods=["POS"])
def send_message():

    message_body = request.json.get("message")
    key = request.json.get("key")
    data = {"key": key, "message": message_body}
    return chat_completion_service.generate_response(data=data), 200

