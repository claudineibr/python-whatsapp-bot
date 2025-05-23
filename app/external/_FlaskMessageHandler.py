import logging

from flask import Flask
from hypercorn.asyncio import serve
from hypercorn.config import Config
import asyncio

from app.config import (
    load_configurations,
    configure_logging,
)
from app.extensions import (
    db,
    migrate,
    async_db,
)
from repository.whatsapp import WhatsAppRepository

logger = logging.getLogger()


class FlaskMessageHandler(object):
    def __init__(self) -> None:
        self.routes = {}
        self.app = None

    async def run(self, host: str = "0.0.0.0", port: int = 8000, debug: bool = False) -> Flask:
        self.create_app()
        self.test_database_connections()
        self.register_route()

        config = Config()
        config.bind = [f"{host}:{port}"]
        print(f"Starting Hypercorn server on {host}:{port} ...")
        await serve(self.app, config)
        #
        # self.app.run(host=host, port=port, debug=debug)
        return self.app

    def create_app(self) -> Flask:
        self.app = Flask(__name__)
        self.configure()
        self.init_database_connection()
        return self.app

    def configure(self) -> None:
        logger.debug("Starting configurations...")
        configure_logging()
        load_configurations(self.app)
        logger.debug("End configurations...")

    def register_route(self) -> None:
        logger.debug("Starting registering routes...")

        logger.debug("Registering whatsapp routes...")
        from app.routes.whatsapp.whatsapp_routes import whatsapp_blueprint
        self.app.register_blueprint(whatsapp_blueprint)
        logger.debug("Registered whatsapp routes...")

        logger.debug("Registering chat_completion routes...")
        from app.routes.chat_completion.chat_completion_routes import chat_completion_blueprint
        self.app.register_blueprint(chat_completion_blueprint)
        logger.debug("Registered chat_completion routes...")

        logger.debug("Registering chat_assistant routes...")
        from app.routes.chat_assistant.chat_assistant_routes import chat_assistant_blueprint
        self.app.register_blueprint(chat_assistant_blueprint)
        logger.debug("Registered chat_assistant routes...")

        logger.debug("End registering routes...")

    def init_database_connection(self) -> None:
        logger.debug("Starting init database connection...")
        db.init_app(app=self.app)
        migrate.init_app(app=self.app, db=db)
        async_db.init_app(app=self.app)
        logger.debug("End database connection...")

    @staticmethod
    def test_database_connections() -> None:
        logger.debug("Starting test database connections...")
        whatsapp_repository = WhatsAppRepository()
        asyncio.run(whatsapp_repository.test_connection())
        logger.debug("End test database connections")
