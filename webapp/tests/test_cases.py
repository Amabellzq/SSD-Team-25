import pytest
from flask import url_for
from werkzeug.security import generate_password_hash
from webapp.model import User, db


def test_register_success(test_client, mocker):
    mocker.patch('webapp.services.UserService.get_by_username', return_value=None)
    mocker.patch('webapp.services.UserService.get_by_email', return_value=None)
    mocker.patch('webapp.services.UserService.create', return_value=True)
    response = test_client.get('/register')
    assert response.status_code == 200
    response = test_client.post('/register', data=dict(
        username='testinguser',
        email='testinguser@gmail.com',
        role='Customer',
        password='TestingPas1w@rd',
        confirm_password='TestingPas1w@rd',
        profile_picture=(None, '')  #
    ), follow_redirects=True)
    print(response.data)
    assert response.status_code == 200
    assert b'Registration Successful' in response.data
def test_register_invalid_email_format(test_client, mocker):
    # Mock the UserService methods
    mocker.patch('webapp.services.UserService.get_by_username', return_value=None)
    mocker.patch('webapp.services.UserService.get_by_email', return_value=None)
    mocker.patch('webapp.services.UserService.create', return_value=True)
    response = test_client.post('/register', data=dict(
        username='testuser',
        email='invalidemail',
        role='Customer',
        password='TestingPas1w@rd',
        confirm_password='TestingPas1w@rd',
        profile_picture=(None, '')
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'Email: Invalid Email' in response.data

def test_register_mismatched_passwords(test_client, mocker):
    mocker.patch('webapp.services.UserService.get_by_username', return_value=None)
    mocker.patch('webapp.services.UserService.get_by_email', return_value=None)
    mocker.patch('webapp.services.UserService.create', return_value=True)
    response = test_client.post('/register', data=dict(
        username='testuser',
        email='newuser@example.com',
        role='Customer',
        password='TestingPas1w@rd',
        confirm_password='MismatchedTestingPas1w@rd',
        profile_picture=(None, '')
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'Confirm Password: Password must match' in response.data

def test_login_invalid_credentials(test_client, mocker):
    mocker.patch('webapp.services.UserService.get_by_username', return_value=None)
    response = test_client.post('/login', data=dict(username='testuser', password='wrongpassword'),
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data
@pytest.fixture(autouse=True)
def run_around_tests():
    yield
    db.session.remove()