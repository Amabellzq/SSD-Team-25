from flask import Flask
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

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Register Blueprint
app.register_blueprint(main)

# To ensure no circular import issues
from .routes import main
