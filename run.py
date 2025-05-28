import logging

from app.external import FastAPIMessageHandler

logger = logging.getLogger(__name__)


if __name__ == "__main__":


    logger.debug("Starting API [{}] ...".format(__name__))

    flask_message_handler = FastAPIMessageHandler(debug=True)
    flask_message_handler.run()

    logger.debug("API [{}] running...".format(__name__))
