from flask import Flask
from config import Config
from .routes import main
from flask_login import LoginManager
from .models import db, User, load_user  # Import your user model

app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = 'ssdT25'

# Initialize SQLAlchemy
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'

@login_manager.user_loader
def user_loader(user_id):
    return load_user(user_id)

# @login_manager.user_loader
# # def load_user(user_id):
# #     return User.get_by_id(user_id)
# def user_loader(user_id):
#     return load_user(user_id)

from .routes import main # Import routes after LoginManager setup to avoid circular imports

app.register_blueprint(main)

# Create database tables
#with app.app_context():
#   db.create_all()