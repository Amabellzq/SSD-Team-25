import pytest
from flask import Flask

from webapp import app, db
from config import TestConfig


@pytest.fixture(scope='module')
def test_client():
    # Configure the app for testing

    app.config.from_object(TestConfig)

    # Create a test client using the Flask application configured in your `__init__.py`
    with app.test_client() as testing_client:
        with app.app_context():
            # Create all tables
            if not hasattr(db, 'app'):
                db.init_app(app)
            db.create_all()
            yield testing_client  # this is where the testing happens
            # Drop all tables
            db.drop_all()


@pytest.fixture(scope='module')
def init_database():
    app.config.from_object(TestConfig)
    # Create the database and the database table(s)
    with app.app_context():
        if not hasattr(db, 'app'):
            db.init_app(app)
        db.create_all()
        yield db  # this is where the testing happens
        db.drop_all()
