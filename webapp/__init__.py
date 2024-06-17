from flask import Flask
from .routes import main

app = Flask(__name__)  # This creates the Flask application instance named 'app'
app.register_blueprint(main)
