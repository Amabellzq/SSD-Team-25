from datetime import timedelta

from flask import Flask
from flask_session import Session

from config import Config
from .routes import main
from flask_login import LoginManager
from .models import db, User  # Import your user model

app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = 'ssdT25'
app.config['DEBUG'] = True  # Enable debug mode

# Initialize SQLAlchemy
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "sqlalchemy"
app.config['SESSION_SQLALCHEMY'] = db
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # Session expires in 1 hour
Session(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Register Blueprint
app.register_blueprint(main)

# Optional: Uncomment if you want to create tables in a new setup
# Create database tables
# with app.app_context():
#    db.create_all()

# To ensure no circular import issues
from .routes import main
