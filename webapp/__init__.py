import socket
import time
from flask import Flask
from config import Config
from .routes import main
from flask_login import LoginManager
from .model import db, User
from flask_wtf.csrf import CSRFProtect
from .services import UserService
from flask_session import Session
from datetime import timedelta
import base64
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key-if-none-found')
app.config['DEBUG'] = True  # Enable debug mode for local development


# Initialize SQLAlchemy
db.init_app(app)

# Configure session settings
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "sqlalchemy"
app.config['SESSION_SQLALCHEMY'] = db
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # Session expires in 1 hour
Session(app)

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'

# Initialize Flask-Limiter for rate limiting
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["100 per day", "25 per hour"])

@login_manager.user_loader
def load_user(user_id):
    return UserService.get(user_id)

# Register Blueprint
app.register_blueprint(main)

# Define the base64 encode filter
def b64encode(value):
    return base64.b64encode(value.encode()).decode('utf-8')

# Register the filter for Jinja templates
app.jinja_env.filters['b64encode'] = b64encode

# To ensure no circular import issues
from .routes import main

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
