from flask import Flask
from .routes import main

app = Flask(__name__)
app.config.from_object('config')
app.register_blueprint(main)