import pytest
from flask import Flask

from webapp import app
from sqlalchemy.testing import db
from config import TestConfig


@pytest.fixture(scope='module')
def test_client():
    # Configure the app for testing

    app.config.from_object(TestConfig)
    # Reinitialize the SQLAlchemy instance to avoid any conflicts

    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            yield testing_client

        # Teardown: drop all tables
            db.session.remove()
            db.drop_all()


@pytest.fixture(scope='module')
def init_database():
    app.config.from_object(TestConfig)
    # Create the database and the database table(s)
    with app.app_context():
        db.create_all()
        yield db  # this is where the testing happens
        db.session.remove()
        db.drop_all()
