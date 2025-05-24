import asyncio
import logging
import sys

import uvicorn
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.extensions import async_db
from app.repository.whatsapp import WhatsAppRepository

logger = logging.getLogger()


class FastAPIMessageHandler(object):
    def __init__(self, debug: bool = False) -> None:
        self.routes = {}
        self.app = self.create_app(debug=debug)
        self.app.add_middleware(
            middleware_class=CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def run(self) -> FastAPI:
        self.test_database_connections()
        self.register_route()
        uvicorn.run(self.app, host="0.0.0.0", port=8000)
        return self.app

    def create_app(self, debug: bool = False) -> FastAPI:
        self.app = FastAPI(
            title="Chat Bot API - AI",
            version="1.0.0",
            debug=debug,
        )
        self.configure()
        self.init_database_connection()
        return self.app

    @staticmethod
    def configure() -> None:
        logger.debug("Starting configurations...")
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            stream=sys.stdout,
        )

        logger.debug("End configurations...")

    def register_route(self) -> None:
        logger.debug("Starting registering routes...")

        logger.debug("Registering whatsapp routes...")
        from app.routes.whatsapp.whatsapp_routes import whatsapp_route
        self.app.include_router(whatsapp_route)
        logger.debug("Registered whatsapp routes...")

        logger.debug("Registering chat_completion routes...")
        from app.routes.chat_completion.chat_completion_routes import chat_completion_blueprint
        self.app.include_router(chat_completion_blueprint)
        logger.debug("Registered chat_completion routes...")

        logger.debug("Registering chat_assistant routes...")
        from app.routes.chat_assistant.chat_assistant_routes import chat_assistant_route
        self.app.include_router(chat_assistant_route)
        logger.debug("Registered chat_assistant routes...")

        logger.debug("End registering routes...")

    @staticmethod
    def init_database_connection() -> None:
        logger.debug("Starting init database connection...")
        async_db.init()
        logger.debug("End database connection...")

    @staticmethod
    def test_database_connections() -> None:
        logger.debug("Starting test database connections...")
        whatsapp_repository = WhatsAppRepository()
        asyncio.run(whatsapp_repository.test_connection())
        logger.debug("End test database connections")
