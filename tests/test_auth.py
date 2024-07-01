import os
import pytest
from flask import url_for
from werkzeug.security import generate_password_hash
from webapp import app, db
from webapp.models import User

# Configuration class for testing
class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_database.db'
    SECRET_KEY = 'test'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SERVER_NAME = 'localhost:5000'  # Assuming Flask runs on port 5000 in the container
    APPLICATION_ROOT = '/'  # Define the root of your application
    PREFERRED_URL_SCHEME = 'http'  # Define the preferred URL scheme

# Fixture to setup the application context and database
@pytest.fixture
def app_context():
    app.config.from_object(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        os.remove('test_database.db')

# Fixture to setup the test client
@pytest.fixture
def client(app_context):
    return app_context.test_client()

# Fixture to initialize the database with test data
@pytest.fixture
def init_database(app_context):
    # Create a test user
    user = User(username='testuser', password=generate_password_hash('testpassword'), role='Customer')
    db.session.add(user)
    db.session.commit()

    yield db  # this is where the testing happens!

    db.session.remove()
    db.drop_all()

# Test for user registration
def test_register_user(client):
    response = client.post(url_for('main.register'), data={
        'username': 'newuser',
        'password': 'newpassword',
        'role': 'Customer',
        'profile_picture': None
    })
    assert response.status_code == 302  # Should redirect to login
    assert b'Thanks for registering!' in response.data

    user = User.query.filter_by(username='newuser').first()
    assert user is not None
    assert user.username == 'newuser'
    assert user.role == 'Customer'

# Test for user login
def test_login_user(client, init_database):
    response = client.post(url_for('main.login'), data={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 302  # Should redirect to home
    assert b'Login successful' in response.data

# Test for user login with invalid password
def test_login_user_invalid_password(client, init_database):
    response = client.post(url_for('main.login'), data={
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 200  # Should stay on login page
    assert b'Invalid username or password' in response.data

# Test for user login with nonexistent username
def test_login_user_nonexistent(client):
    response = client.post(url_for('main.login'), data={
        'username': 'nonexistent',
        'password': 'password'
    })
    assert response.status_code == 200  # Should stay on login page
    assert b'Invalid username or password' in response.data
