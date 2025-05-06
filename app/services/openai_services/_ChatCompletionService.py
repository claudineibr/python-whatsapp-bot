import json

from typing import (
    Dict,
    Callable,
)
from functools import cache
from ._OpenAIServicesBase import OpenAIServicesBase

json_data = None
session_data = {}


@cache
class ChatCompletionService(OpenAIServicesBase):
    def __init__(self) -> None:
        super().__init__()

        global json_data
        if json_data is None:
            self._build_data()

    @staticmethod
    def _build_data() -> None:

        global json_data
        if json_data is None:
            with open('data/json_data.json', 'r', encoding='utf-8') as file:
                json_data = json.loads(file.read())

    def generate_response(self, data: Dict[str, str], callback: Callable[[str, str], str] = None) -> str:

        message = self.process_text(text=data.get("message"))
        key = data.get("key")
        self.input_validate(message=message)

        if key not in session_data:
            initial_prompt = self._initial_prompt(data)
            session_data[key] = [
                {"role": "system", "content": initial_prompt}
            ]

        session_data[key].append({"role": "user", "content": message})
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=session_data[key],
            temperature=0.8,
        )
        response_message = response.choices[0].message.content.strip()
        session_data[key].append({"role": "assistant", "content": response_message})
        return response_message

    def _initial_prompt(self, data: Dict[str, str]) -> str | bytes:
        global json_data

        if json_data is None:
            return "Você é um assistente virtual da empresa"

        instructions = "\n".join((json_data or {}).get("systemInstructions"))
        system_data = (json_data or {}).get("systemData", "")
        extra_data = (data or {}).get("extraData", "")
        instructions = instructions.replace("{{extraData}}", extra_data)
        instructions = instructions.replace("{{systemData}}", json.dumps(system_data))
        return self.process_text(text=instructions)

    @staticmethod
    def load_history(session_id, limit=10):
        pass
