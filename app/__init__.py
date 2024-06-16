import logging
from flask import Flask
from .routes import main


def create_app():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    app = Flask(__name__)

    try:
        app.register_blueprint(main)
        logger.info("Flask application has been created successfully")
    except Exception as e:
        logger.error(f"Error creating Flask application: {e}")
        raise e

    return app
s