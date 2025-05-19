import logging

from flask import (
    Blueprint,
    request,
)

from app.services.openai_services import ChatCompletionService

logger = logging.getLogger(__name__)

chat_completion_service = ChatCompletionService()
chat_completion_blueprint = Blueprint(name="chat_completion", import_name=__name__, url_prefix="/openai")

@chat_completion_blueprint.route(rule="/chat_completion/send_message", methods=["POST"])
async def send_message():

    message_body = request.json.get("message")
    key = request.json.get("key")
    data = {"key": key, "message": message_body}
    response = await chat_completion_service.send_message(data)
    return response, 200

