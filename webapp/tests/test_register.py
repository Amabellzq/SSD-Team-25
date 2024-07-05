import pytest
from flask import url_for
from webapp.model import User


def test_register_success(test_client, mocker):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/register' page is posted to (POST)
    THEN check if a new user is registered successfully
    """
    mock_create_user = mocker.patch('webapp.services.UserService.create', return_value=User(
        username='newuser', email='newuser@example.com', password='hashed_password', role='Customer'
    ))

    response = test_client.post(url_for('main.register'), data=dict(
        username='newuser',
        email='newuser@example.com',
        role='Customer',
        password='password',
        confirm_password='password'
    ), follow_redirects=True)

    assert response.status_code == 200
    assert b'Registration Successful' in response.data
    mock_create_user.assert_called_once_with(username='newuser', email='newuser@example.com', password='password',
                                             role='Customer')


def test_register_duplicate_username(test_client, mocker):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/register' page is posted to with an existing username (POST)
    THEN check if the appropriate error message is returned
    """
    mock_get_by_username = mocker.patch('webapp.services.UserService.get_by_username', return_value=User(
        username='newuser', email='newuser@example.com'
    ))

    response = test_client.post(url_for('main.register'), data=dict(
        username='newuser',
        email='newuser@example.com',
        role='Customer',
        password='password',
        confirm_password='password'
    ), follow_redirects=True)

    assert response.status_code == 200
    assert b'Username already exists. Please choose a different username.' in response.data
    mock_get_by_username.assert_called_once_with('newuser')
