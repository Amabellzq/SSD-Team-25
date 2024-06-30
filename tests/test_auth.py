import pytest
from flask import url_for
from werkzeug.security import generate_password_hash
from webapp import app, db
from webapp.models import User

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

@pytest.fixture
def app_context():
    app.config.from_object(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app_context):
    return app_context.test_client()

@pytest.fixture
def init_database(app_context):
    # Create a test user
    user = User(username='testuser', password=generate_password_hash('testpassword'), role='Customer')
    db.session.add(user)
    db.session.commit()

    yield db  # this is where the testing happens!

    db.session.remove()
    db.drop_all()

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

def test_login_user(client, init_database):
    response = client.post(url_for('main.login'), data={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 302  # Should redirect to home
    assert b'Login successful' in response.data

def test_login_user_invalid_password(client, init_database):
    response = client.post(url_for('main.login'), data={
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 200  # Should stay on login page
    assert b'Invalid username or password' in response.data

def test_login_user_nonexistent(client):
    response = client.post(url_for('main.login'), data={
        'username': 'nonexistent',
        'password': 'password'
    })
    assert response.status_code == 200  # Should stay on login page
    assert b'Invalid username or password' in response.data
