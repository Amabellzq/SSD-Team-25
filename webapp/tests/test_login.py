import pytest
from flask import url_for
from werkzeug.security import generate_password_hash
from webapp.model import User, db


def test_register_success(test_client, mocker):
    # Mock the UserService methods
    mocker.patch('webapp.services.UserService.get_by_username', return_value=None)
    mocker.patch('webapp.services.UserService.get_by_email', return_value=None)
    mocker.patch('webapp.services.UserService.create', return_value=True)

    # Simulate form submission
    response = test_client.post('/register', data=dict(
        username='testuser',
        email='newuser@example.com',
        password='testpassword',
        role='Customer',
        profile_picture=(None, '')  # Mock profile picture as empty
    ), follow_redirects=True)

    # Assert the response status code
    assert response.status_code == 200

    # Assert that the success message is in the response data
    assert b'Registration Successful' in response.data


def test_login_success(test_client, mocker):
    # Mock UserService.get_by_username to return a user
    mock_user = User(username='testuser', password=generate_password_hash('testpassword'))
    mocker.patch('webapp.services.UserService.get_by_username', return_value=mock_user)
    mocker.patch('webapp.routes.check_password_hash', return_value=True)  # Mock check_password_hash

    response = test_client.post('/login', data=dict(username='testuser', password='testpassword'),
                                follow_redirects=True)

    assert response.status_code == 200
    assert b'TOTP' in response.data or b'verify_totp' in response.data  # Adjust this as needed based on your TOTP flow


def test_login_invalid_credentials(test_client, mocker):
    # Mock UserService.get_by_username to return None (user not found)
    mocker.patch('webapp.services.UserService.get_by_username', return_value=None)

    response = test_client.post('/login', data=dict(username='testuser', password='wrongpassword'),
                                follow_redirects=True)

    assert response.status_code == 200
    assert b'Invalid username or password' in response.data

# def test_add_to_cart_product_not_found(test_client, mocker):
#     mock_get_product = mocker.patch('webapp.services.ProductService.get', return_value=None)
#     response = test_client.post(url_for('main.add_to_cart', product_id=1), data=dict(quantity=1), follow_redirects=True)
#     assert response.status_code == 200
#     assert b'Product not found' in response.data
#     mock_get_product.assert_called_once_with(1)

@pytest.fixture(autouse=True)
def run_around_tests():
    # Setup before each test
    yield
    # Teardown after each test
    db.session.remove()