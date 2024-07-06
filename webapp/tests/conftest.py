import pytest
from flask import Flask

from webapp import app, db
from config import TestConfig


@pytest.fixture(scope='module')
def test_client():
    # Configure the app for testing

    app.config.from_object(TestConfig)
    with app.app_context():
        db.create_all()

    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client

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
