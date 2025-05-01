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
        load_configurations(self.app)
        configure_logging()
        logger.debug("End configurations...")


    def register_route(self) -> None:

        logger.debug("Starting registering routes...")

        from app.routes.whatsapp.whatsapp_routes import whatsapp_blueprint
        self.app.register_blueprint(whatsapp_blueprint)

        from app.routes.chat_completion.chat_completion_routes import chat_completion_blueprint
        self.app.register_blueprint(chat_completion_blueprint)

        logger.debug("End registering routes...")
