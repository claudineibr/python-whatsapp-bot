import datetime
import logging

from fastapi import APIRouter, Request
from jwt import jwt

from app.services.openai_services import ChatAssistantService
from app.config.settings import get_settings
settings = get_settings()
logger = logging.getLogger(__name__)

chat_assistant_service = ChatAssistantService()
login_blueprint = APIRouter(prefix="/authorization")


@login_blueprint.post(path="/login")
async def login(request: Request):
    data = await request.json()
    user = data.get('userName')
    password = data.get('password')

    response = generate_authorization_token(user_id=1)
    return response, 200


def generate_authorization_token(user_id: int):
    payload = {
        'person_id': user_id,
        'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=2),
        'iat': datetime.datetime.now(datetime.UTC)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token
