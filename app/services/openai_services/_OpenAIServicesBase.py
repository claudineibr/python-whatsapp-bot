import os
import httpx
import re

from abc import abstractmethod
from typing import Dict, Callable

from openai import AsyncOpenAI
from fastapi import HTTPException


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
    async def generate_response(self, data: Dict[str, str], callback: Callable[[str, str], str] = None) ->  str:
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
            raise HTTPException(status_code=400, detail="No data reported..")
        if len(message) > 500:
            raise HTTPException(status_code=400, detail="Question too long (max 500 characters)")
