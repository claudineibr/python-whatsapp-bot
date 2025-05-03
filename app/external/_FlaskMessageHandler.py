import logging

from flask import Flask

from app.config import (
    load_configurations,
    configure_logging,
)

logger = logging.getLogger()


class FlaskMessageHandler(object):
    def __init__(self) -> None:

        self.routes = {}
        self.app = None

    def run(self, name: str, host: str, port: int, debug: bool = False) -> Flask:

        self.app = Flask(name)
        self.configure()
        self.register_route()
        self.app.run(host=host, port=port, debug=debug)
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
