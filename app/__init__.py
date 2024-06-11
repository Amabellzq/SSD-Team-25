from flask import Flask, g, redirect, url_for
from flask_login import LoginManager, current_user
from flask_principal import Principal, Identity, AnonymousIdentity, identity_loaded, identity_changed, RoleNeed
from flask_session import Session
from .config import Config
from .extensions import db_admin, db_user, db_readonly, login_manager, principals, session
from .routes import main_blueprint


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    login_manager.init_app(app)
    principals.init_app(app)
    session.init_app(app)

    # Register blueprints
    app.register_blueprint(main_blueprint)

    @app.before_request
    def set_db_connection():
        if not current_user.is_authenticated:
            return redirect(url_for('main.login'))

        # Determine which database connection to use based on the user's role
        if current_user.role == 'Admin':
            app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI_ADMIN
            g.db = db_admin
        elif current_user.role == 'Merchant':
            app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI_USER
            g.db = db_user
        else:
            app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI_READONLY
            g.db = db_readonly

        g.db.init_app(app)
        g.db.session.commit()

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        # Set the identity user object
        identity.user = current_user

        # Add the UserNeed to the identity
        if hasattr(current_user, 'user_id'):
            identity.provides.add(Identity(current_user.user_id))

        # Add each role to the identity
        if hasattr(current_user, 'role'):
            identity.provides.add(RoleNeed(current_user.role))

    return app
