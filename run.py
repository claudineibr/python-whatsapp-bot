import logging

from app.external import FlaskMessageHandler

logger = logging.getLogger(__name__)

if __name__ == "__main__":

    logger.debug("Starting flask [{}] ...".format(__name__))

    flask_message_handler = FlaskMessageHandler()
    flask_message_handler.run(host="0.0.0.0", port=8000, debug=True)

    logger.debug("Flask [{}] running...".format(__name__))
