from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_principal import Principal
from flask_session import Session

# Databases for different user roles
db_admin = SQLAlchemy()
db_user = SQLAlchemy()
db_readonly = SQLAlchemy()

# Other extensions
migrate = Migrate()
login_manager = LoginManager()
principals = Principal()
session = Session()
