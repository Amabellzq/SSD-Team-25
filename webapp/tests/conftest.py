import pytest
from flask import Flask

from webapp import db
from config import TestConfig
from webapp.model import User


@pytest.fixture(scope='module')
def test_client():
    app = Flask(__name__)
    app.config.from_object(TestConfig)
    # Ensure the SQLAlchemy instance is properly initialized
    db.init_app(app)

    # Create a test client using the Flask application configured for testing
    with app.test_client() as testing_client:
        with app.app_context():
            # Create all tables
            db.create_all()
            yield testing_client  # this is where the testing happens

            # Drop all tables
            db.drop_all()


@pytest.fixture(scope='module')
def init_database():
    # Create the database and the database table
    db.create_all()

    # Insert user data
    user1 = User(username='testuser', email='test@example.com', password='password', role='Customer')
    db.session.add(user1)

    # Commit the changes for the users
    db.session.commit()

    yield db  # this is where the testing happens

    db.session.remove()
    db.drop_all()
