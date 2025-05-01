import requests
import logging
import json

from functools import cache


from typing import Dict, Any

from flask import (
    current_app,
    jsonify,
)
from requests import Response

from app.services.openai_services import ChatCompletionService

logger = logging.getLogger(__name__)

@cache
class WhatsAppServices(object):
    def __init__(self, open_ai_chat: ChatCompletionService) -> None:

        self.open_ai_chat = open_ai_chat

    def process_whatsapp_message_with_open_ai(self, body: Dict[str, Any]):

        wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
        name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]
        message = body["entry"][0]["changes"][0]["value"]["messages"][0]
        message_body = message["text"]["body"]

        data = {"key": wa_id, "name": name, "message": message_body}
        response = self.open_ai_chat.generate_response(data=data)
        data = self.__get_text_message_input(recipient=wa_id, text=response)
        return self.__send_message(data=data)

    def send_message(self, message: str) -> tuple[Response, int] | Response:
        data = self.__get_text_message_input(current_app.config["RECIPIENT_WAID"], message)
        return self.__send_message(data)

    def __send_message(self, data) -> tuple[Response, int] | Response:
        try:
            headers = {
                "Content-type": "application/json",
                "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
            }
            url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"
            response = requests.post(
                url=url,
                data=data,
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()
        except requests.Timeout:
            logger.error("Timeout occurred while sending message")
            return jsonify({"status": "error", "message": "Request timed out"}), 408
        except requests.RequestException as e:  # This will catch any general request exception
            logger.error(f"Request failed due to: {e}")
            return jsonify({"status": "error", "message": "Failed to send message"}), 500
        else:
            self.__log_http_response(response=response)
            return response

    @staticmethod
    def __get_text_message_input(recipient: str, text: str):
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
    def __log_http_response(response: Response):
        logger.debug(f"Status: {response.status_code}")
        logger.debug(f"Content-type: {response.headers.get('content-type')}")
        logger.debug(f"Body: {response.text}")
