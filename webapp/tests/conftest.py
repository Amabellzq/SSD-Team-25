import pytest
from webapp import create_app, db
from webapp.config import TestConfig
from webapp.models import User


@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app(TestConfig)

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
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
