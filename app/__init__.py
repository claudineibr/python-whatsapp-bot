# import logging
#
# from flask import Flask
# from app.config import (
#     load_configurations,
#     configure_logging,
# )
# from app.services.openai_services import ChatCompletionService
# from app.services.whatsapp_services import WhatsAppServices
#
#
# def create_app():
#     app = Flask(__name__)
#
#     # Load configurations and logging settings
#     load_configurations(app)
#     configure_logging()
#
#     logger = logging.getLogger(__name__)
#     logger.debug("Starting Build Singletons...")
#     # Build Singletons
#     # ChatCompletionService()
#     # WhatsAppServices()
#     logger.debug("End Build Singletons...")
#
#     # Import and register blueprints, if any
#     from app.routes.whatsapp.whatsapp_routes import whatsapp_blueprint
#     app.register_blueprint(whatsapp_blueprint)
#
#     return app
# #
