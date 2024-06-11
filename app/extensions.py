from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_principal import Principal
from flask_session import Session

# Create SQLAlchemy instances
db_admin = SQLAlchemy()
db_user = SQLAlchemy()
db_readonly = SQLAlchemy()

# Initialize Flask-Login
login_manager = LoginManager()

# Initialize Flask-Principal
principals = Principal()

# Initialize Flask-Session
session = Session()
