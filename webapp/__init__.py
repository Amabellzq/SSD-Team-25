from flask import Flask
from .routes import main
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from .models import User, load_user  # Import your user model

app = Flask(__name__)
app.config.from_object('config')
app.config['SECRET_KEY'] = 'ssdT25'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

from .routes import main # Import routes after LoginManager setup to avoid circular imports
app.register_blueprint(main)
