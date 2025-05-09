import os
import httpx
import re

from abc import abstractmethod
from typing import Dict, Callable

from flask import abort
from openai import AsyncOpenAI


class OpenAIServicesBase(object):
    def __init__(self):

        self.openai_assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.client = AsyncOpenAI(
            api_key=self.openai_api_key,
            timeout=httpx.Timeout(
                timeout=60,
                connect=5.0,
            ),
        )

    @abstractmethod
    async def generate_response(self, data: Dict[str, str], callback: Callable[[str, str], str] = None) -> Dict[
        str, int]:
        raise NotImplementedError()

    @staticmethod
    def process_text(text: str) -> str:
        pattern = r"\【.*?\】"
        text = re.sub(pattern, "", text).strip()
        pattern = r"\*\*(.*?)\*\*"
        replacement = r"*\1*"
        return re.sub(pattern, replacement, text)

    @staticmethod
    def input_validate(message: str) -> None:
        if not message or not message.strip():
            raise abort(code=400, description="Nenhum dado informado.")
        if len(message) > 500:
            raise abort(code=400, description="Pergunta muito longa (máx. 500 caracteres)")
