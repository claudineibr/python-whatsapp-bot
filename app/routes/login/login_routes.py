import datetime
import logging

from flask import (
    Blueprint,
    current_app,
    request,
)

from app.services.openai_services import ChatAssistantService

logger = logging.getLogger(__name__)

chat_assistant_service = ChatAssistantService()
login_blueprint = Blueprint("login", import_name=__name__, url_prefix="/authorization")

@login_blueprint.route(rule="/login", methods=["POST"])
async def login():
    data = request.get_json()
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
    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm='HS256')
    return token
