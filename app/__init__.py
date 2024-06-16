import logging
from flask import Flask
from .routes import main


def create_app():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    app = Flask(__name__)
    app.register_blueprint(main)

    logger.info("Flask application has been created successfully")

    return app
