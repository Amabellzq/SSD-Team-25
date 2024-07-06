import pytest
from flask import Flask

from webapp import app, db
from config import TestConfig


@pytest.fixture(scope='module')
def test_client():
    # Configure the app for testing
    app.config.from_object(TestConfig)
    # Ensure the db is only initialized once
    with app.app_context():
        db.init_app(app)
        db.create_all()

    # Create a test client using the Flask application configured in your `__init__.py`
    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client  # this is where the testing happens

    # Teardown phase
    with app.app_context():
        db.drop_all()
        db.session.remove()


@pytest.fixture(scope='module')
def init_database():
    app.config.from_object(TestConfig)
    # Create the database and the database table(s)
    with app.app_context():
        db.create_all()
        yield db  # this is where the testing happens

        db.drop_all()
        db.session.remove()
