from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def role_required(role):
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
