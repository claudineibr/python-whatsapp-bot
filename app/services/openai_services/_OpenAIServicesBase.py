import os
import re
from abc import abstractmethod
from typing import Dict

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class OpenAIServicesBase(object):
    def __init__(self):

        self.openai_assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.openai_api_key)

    @abstractmethod
    def generate_response(self, data: Dict[str, str]) -> str:
        raise NotImplementedError()

    @staticmethod
    def process_text(text: str) -> str:
        pattern = r"\【.*?\】"
        text = re.sub(pattern, "", text).strip()
        pattern = r"\*\*(.*?)\*\*"
        replacement = r"*\1*"
        whatsapp_style_text = re.sub(pattern, replacement, text)
        return whatsapp_style_text
