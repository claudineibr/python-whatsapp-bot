import requests
import logging
import json
import os

from functools import cache

from typing import Dict, Any

from fastapi import HTTPException, status
from requests import Response
from app.services.openai_services import ChatCompletionService
from app.schemas import WhatsAppChatMessageCreate, WhatsAppChatMessageUpdate
from app.repository.whatsapp import WhatsAppRepository

logger = logging.getLogger(__name__)


@cache
class WhatsAppServices(object):
    def __init__(self, open_ai_chat: ChatCompletionService) -> None:

        self.open_ai_chat = open_ai_chat
        self.repository = WhatsAppRepository()

    async def process_whatsapp_message_with_open_ai(self, body: Dict[str, Any]) -> Response:

        message = self.__build_receive_message(body=body)
        data = {"key": message.phone, "name": message.name, "message": message.message}
        response = await self.open_ai_chat.generate_response(data=data)
        data = self.__get_text_message_input(recipient=message.phone, text=response)
        return self.__send_message(data=data)

    async def send_message(self, message: str) -> Response:
        data = self.__get_text_message_input(os.getenv("RECIPIENT_WAID"), message)
        return self.__send_message(data=data)

    async def create_message(self, body: Dict[str, Any]) -> None:
        try:
            message = self.__build_receive_message(body=body)
            await self.repository.create_message(message=message)
        except:
            logger.exception("Failed to create message")
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Failed to send message")

    async def update_status(self, body: Dict[str, Any]) -> None:
        try:
            message = WhatsAppChatMessageUpdate(
                message_id=body["message"]["message_id"],
                status=body["entry"][0]["changes"][0]["value"]["status"],
                mark_as=body["entry"][0]["changes"][0]["value"]["mark_as"],
            )
            await self.repository.update_status_message(message=message)
        except:
            logger.exception("Failed to update message")
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Failed to send message")

    def __send_message(self, data: str) -> Response:
        try:
            headers = {
                "Content-type": "application/json",
                "Authorization": f"Bearer {os.getenv('ACCESS_TOKEN')}",
            }
            url = f"https://graph.facebook.com/{os.getenv("VERSION")}/{os.getenv("PHONE_NUMBER_ID")}/messages"
            response = requests.post(
                url=url,
                data=data,
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()
        except requests.Timeout:
            logger.error("Timeout occurred while sending message")
            raise HTTPException(status_code=408, detail="Timeout occurred while sending message")
        except requests.RequestException as e:  # This will catch any general request exception
            logger.error(f"Request failed due to: {e}")
            raise HTTPException(status_code=408, detail="Failed to send message")
        else:
            self.__log_http_response(response=response)
            return response

    @staticmethod
    def __get_text_message_input(recipient: str, text: str) -> str:
        return json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient,
                "type": "text",
                "text": {"preview_url": False, "body": text},
            }
        )

    @staticmethod
    def is_valid_whatsapp_message(body: Dict[str, Any]) -> bool:
        return (
            body.get("object")
            and body.get("entry")
            and body["entry"][0].get("changes")
            and body["entry"][0]["changes"][0].get("value")
            and body["entry"][0]["changes"][0]["value"].get("messages")
            and body["entry"][0]["changes"][0]["value"]["messages"][0]
        )

    @staticmethod
    def __log_http_response(response: Response) -> None:
        logger.debug(f"Status: {response.status_code}")
        logger.debug(f"Content-type: {response.headers.get('content-type')}")
        logger.debug(f"Body: {response.text}")

    def __build_receive_message(self, body: Dict[str, Any]) -> WhatsAppChatMessageCreate:
        wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
        name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]
        message = body["entry"][0]["changes"][0]["value"]["messages"][0]
        message_body = message["text"]["body"]
        message_id = message["id"]
        message_type = message["type"]

        return WhatsAppChatMessageCreate(
            phone=wa_id,
            name=name,
            message_type=message_type,
            message_id=message_id,
            message=message_body,
        )
