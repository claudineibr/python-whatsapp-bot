import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.services.openai_services import ChatCompletionService

logger = logging.getLogger(__name__)

chat_completion_service = ChatCompletionService()
chat_completion_route = APIRouter(prefix="/openai")


@chat_completion_route.post(path="/chat_completion/send_message")
async def send_message(request: Request):
    request = await request.json()
    message_body = request.get("message")
    key = request.get("key")
    data = {"key": key, "message": message_body}
    response = await chat_completion_service.send_message(data)
    return JSONResponse(content=response)
