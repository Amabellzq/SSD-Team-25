from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

from config import Config
from webapp import app, db


def role_required(role):
    user_role = current_user.role
    print(user_role)
    db_uri = Config.get_db_uri(user_role)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    db.engine.dispose()  # Dispose the current engine to reset the connection with the new URI
    def decorator(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('main.login'))
            if current_user.role != role:
                print("You do not have access to this resource.")
                return redirect(url_for('main.error404'))
            return func(*args, **kwargs)
        return decorated_view
    return decorator
