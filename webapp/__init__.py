import socket
import time
from flask import Flask, current_app
from config import Config
from .routes import main
from flask_login import LoginManager, current_user
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
app.config['DEBUG'] = True  # Enable debug mode


def wait_for_db(host, port):
    retries = 5
    while retries > 0:
        try:
            # Attempt to create a socket connection to the database
            sock = socket.create_connection((host, port), timeout=5)
            sock.close()
            print("Database is up and running.")
            break
        except (socket.timeout, socket.error) as e:
            print(f"Database not ready yet. Retrying... ({retries} attempts left)")
            retries -= 1
            time.sleep(5)
    if retries == 0:
        raise Exception("Database is not reachable. Exiting.")


# Wait for the database to be ready
wait_for_db('db', 3306)  # 'db' is the service name defined in docker-compose.yml


# Function to dynamically select the database URI
def get_db_uri(user_type=None):
    if user_type == 'Admin':
        return current_app.config['SQLALCHEMY_ADMIN_DATABASE_URI']
    elif user_type == 'Merchant':
        return current_app.config['SQLALCHEMY_MERCHANT_DATABASE_URI']
    elif user_type == 'Customer':
        return current_app.config['SQLALCHEMY_USER_DATABASE_URI']
    elif user_type is None:
        return current_app.config['SQLALCHEMY_READONLY_DATABASE_URI']
    else:
        return current_app.config['SQLALCHEMY_READONLY_DATABASE_URI']


app.config['SQLALCHEMY_DATABASE_URI'] = get_db_uri(None)  # Set to readonly as default

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

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'

# Initialize flask limiter
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["100 per day", "25 per hour"])


@login_manager.user_loader
def load_user(user_id):
    return UserService.get(user_id)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        # Assuming 'role' is an attribute of your User model that defines the user type
        user_role = current_user.role
        app.config['SQLALCHEMY_DATABASE_URI'] = get_db_uri(user_role)
        db.engine.dispose()  # Dispose the current engine to reset the connection with the new URI
        db.init_app(app)


# Register Blueprint
app.register_blueprint(main)


# Optional: Uncomment if you want to create tables in a new setup
# Create database tables
# with app.app_context():
#    db.create_all()

# Define the base64 encode filter
def b64encode(value):
    return base64.b64encode(value).decode('utf-8')


# Register the filter
app.jinja_env.filters['b64encode'] = b64encode

# To ensure no circular import issues
from .routes import main

if __name__ == '__main__':
    app.run(debug=True)
