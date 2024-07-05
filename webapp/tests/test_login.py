import pytest
from flask import url_for
from werkzeug.security import generate_password_hash
from webapp.model import User


def test_login_success(test_client, init_database, mocker):
    mocker.patch('webapp.services.UserService.get_by_username', return_value=User(username='testuser', password=generate_password_hash('testpassword')))
    mocker.patch('webapp.services.UserService.check_password', return_value=True)
    response = test_client.post('/login', data=dict(username='testuser', password='testpassword'), follow_redirects=True)
    assert response.status_code == 200
    assert b'Logout' in response.data

    response = test_client.post(url_for('main.login'), data=dict(
        username='testuser',
        password='password'
    ), follow_redirects=True)

    assert response.status_code == 200
    assert b'Login successful' in response.data
    mock_get_user.assert_called_once_with('testuser')


def test_login_invalid_credentials(test_client, init_database, mocker):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to with invalid credentials (POST)
    THEN check if the appropriate error message is returned
    """
    mock_get_user = mocker.patch('webapp.services.UserService.get_by_username', return_value=None)

    response = test_client.post(url_for('main.login'), data=dict(
        username='testuser',
        password='wrongpassword'
    ), follow_redirects=True)

    assert response.status_code == 200
    assert b'Invalid username or password' in response.data
    mock_get_user.assert_called_once_with('testuser')
