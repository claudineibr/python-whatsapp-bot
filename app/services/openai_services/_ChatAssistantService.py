import os
import shelve
import logging
import time

from json import JSONDecodeError

from typing import (
    Dict,
    Optional,
    List,
    Callable,
)
from functools import cache
from openai.types.beta import Thread
from openai.types.beta.threads import Run

from ._OpenAIServicesBase import OpenAIServicesBase

OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
logger = logging.getLogger(__name__)


@cache
class ChatAssistantService(OpenAIServicesBase):
    def __init__(self) -> None:
        super().__init__()

    def generate_response(self, data: Dict[str, str], callback: Callable[[str, str], str] = None) -> Dict[str, int]:

        message = self.process_text(text=data.get("message"))
        self.input_validate(message=message)

        key = data.get("key")
        thread_id = self.check_if_thread_exists(key=key)

        if thread_id is None:
            logging.info(f"Creating new thread for key {key}")
            thread = self.client.beta.threads.create()
            self.store_thread(key=key, thread_id=thread.id)
            thread_id = thread.id
        else:
            logging.info(f"Retrieving existing thread for key {key}")
            thread = self.client.beta.threads.retrieve(thread_id=thread_id)

        self.create_message(thread_id=thread_id, message=message)

        new_message = self.run_assistant(thread=thread, callback=callback)
        return new_message

    def create_message(self, thread_id: str, message: str, retry: int = 3) -> None:

        while retry > 0:
            try:
                self.client.beta.threads.messages.create(
                    thread_id=thread_id,
                    role="user",
                    content=message,
                )
                retry = 0
            except Exception as e:
                logger.error(f"Failed to create message for thread {thread_id}: {e}")
                self.cancel_run_if_active(thread_id=thread_id)
                retry -= 1

    def run_assistant(self, thread: Thread, callback: Callable[[str, str], str] = None) -> Dict[str, int]:

        assistant = self.client.beta.assistants.retrieve(OPENAI_ASSISTANT_ID)
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
            model="gpt-3.5-turbo",
            poll_interval_ms=5000,
            timeout=60.0
        )

        if run.status == "requires_action":
            if callback is None:
                self.cancel_run_if_active(thread_id=thread.id)
                return {"response": "Callback cannot be None", "status_code": 400}

            run = self.handle_requires_action(run=run, thread_id=thread.id, callback=callback)

        if run.status == "completed":
            response_message = self.get_response(thread_id=run.thread_id)
            logger.info(f"Generated message: {response_message}")
            return {"response": response_message, "status_code": 200}

        if run.status in ["expired", "failed", "cancelled", "incomplete"]:
            return {"response": run.last_error.message, "status_code": 500}

        return {"response": "Not found data", "status_code": 404}

    def get_response(self, thread_id: str):

        messages = self.client.beta.threads.messages.list(thread_id=thread_id)
        message_content = messages.data[0].content[0].text
        annotations = message_content.annotations
        for annotation in annotations:
            message_content.value = message_content.value.replace(annotation.text, '')

        return message_content.value

    @staticmethod
    def check_if_thread_exists(key: str) -> Optional[str]:

        with shelve.open("threads_db") as threads_shelf:
            return threads_shelf.get(key, None)

    @staticmethod
    def store_thread(key: str, thread_id: str) -> None:

        with shelve.open("threads_db", writeback=True) as threads_shelf:
            threads_shelf[key] = thread_id

    def cancel_run_if_active(self, thread_id: str, wait_interval: int = 1):

        runs = self.client.beta.threads.runs.list(thread_id=thread_id)
        if not runs.data:
            return False

        run = runs.data[0]
        if run.status in ["queued", "in_progress", "cancelling", "requires_action"]:
            logger.debug(f"Cancelling run {run.id} (status: {run.status})")
            self.client.beta.threads.runs.cancel(run_id=run.id, thread_id=thread_id)

            while True:
                run = self.client.beta.threads.runs.retrieve(run_id=run.id, thread_id=thread_id)
                if run.status in ["cancelled", "failed", "completed", "expired"]:
                    logger.debug(f"Cancelling run {run.id} (status: {run.status})")
                    return True

                time.sleep(wait_interval)

        return False

    def handle_requires_action(self, run: Run, thread_id: str, callback: Callable[[str, str], str] = None) -> Run:

        tool_outputs = []
        logger.debug(f"Calling required actions with function {callback.__name__}")
        for tool in run.required_action.submit_tool_outputs.tool_calls:
            try:
                response = callback(tool.function.name, tool.function.arguments)
                tool_outputs.append({"tool_call_id": tool.id, "output": response})
            except JSONDecodeError as e:
                logger.error(f"Error processing tool output: {e}")
                tool_outputs.append({"tool_call_id": tool.id, "output": f"JSONDecodeError: {e} "})
            except KeyError as e:
                logger.error(f"Key {e} not found in tool outputs")
                tool_outputs.append({"tool_call_id": tool.id, "output": f"Missing required argument: {e}"})

        run = self.submit_tool_outputs(tool_outputs=tool_outputs, thread_id=thread_id, run_id=run.id)
        while run.status not in ["completed", "failed", "cancelled", "expired"]:

            if run.status == 'requires_action':
                run = self.handle_requires_action(run=run, thread_id=thread_id, callback=callback)

            run = self.client.beta.threads.runs.poll(
                thread_id=thread_id,
                run_id=run.id
            )

        return run

    def submit_tool_outputs(self, tool_outputs: List[Dict[str, str]], thread_id: str, run_id: str) -> Run:

        try:
            return self.client.beta.threads.runs.submit_tool_outputs_and_poll(
                thread_id=thread_id,
                run_id=run_id,
                tool_outputs=tool_outputs
            )
        except Exception as e:
            logger.error(f"Error submitting tool outputs: {e}")
            raise e
