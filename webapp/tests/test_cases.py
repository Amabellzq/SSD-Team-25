import pytest
from flask import url_for
from werkzeug.security import generate_password_hash
from webapp.model import User, db


def test_register_success(test_client, mocker):
    # Mock the UserService methods
    mocker.patch('webapp.services.UserService.get_by_username', return_value=None)
    mocker.patch('webapp.services.UserService.get_by_email', return_value=None)
    mocker.patch('webapp.services.UserService.create', return_value=True)

    # Simulate GET request to load the registration page
    response = test_client.get('/register')
    assert response.status_code == 200

    # Simulate form submission via POST request
    response = test_client.post('/register', data=dict(
        username='testinguser',
        email='testinguser@gmail.com',
        role='Customer',
        password='TestingPas1w@rd',
        confirm_password='TestingPas1w@rd',  # Ensure confirm_password matches
        profile_picture=(None, '')  # Mock profile picture as empty
    ), follow_redirects=True)

    # Print the response data for debugging
    print(response.data)

    # Assert the response status code
    assert response.status_code == 200

    # Assert that the success message is in the response data
    assert b'Registration Successful' in response.data
def test_register_invalid_email_format(test_client, mocker):
    # Mock the UserService methods
    mocker.patch('webapp.services.UserService.get_by_username', return_value=None)
    mocker.patch('webapp.services.UserService.get_by_email', return_value=None)
    mocker.patch('webapp.services.UserService.create', return_value=True)

    # Simulate form submission via POST request
    response = test_client.post('/register', data=dict(
        username='testuser',
        email='invalidemail',
        role='Customer',
        password='TestingPas1w@rd',
        confirm_password='TestingPas1w@rd',
        profile_picture=(None, '')  # Mock profile picture as empty
    ), follow_redirects=True)

    # Assert the response status code
    assert response.status_code == 200

    # Assert that the error message is in the response data
    assert b'Email: Invalid Email' in response.data

def test_register_mismatched_passwords(test_client, mocker):
    # Mock the UserService methods
    mocker.patch('webapp.services.UserService.get_by_username', return_value=None)
    mocker.patch('webapp.services.UserService.get_by_email', return_value=None)
    mocker.patch('webapp.services.UserService.create', return_value=True)

    # Simulate form submission via POST request
    response = test_client.post('/register', data=dict(
        username='testuser',
        email='newuser@example.com',
        role='Customer',
        password='TestingPas1w@rd',
        confirm_password='MismatchedTestingPas1w@rd',
        profile_picture=(None, '')  # Mock profile picture as empty
    ), follow_redirects=True)

    # Assert the response status code
    assert response.status_code == 200

    # Assert that the error message is in the response data
    assert b'Confirm Password: Password must match' in response.data

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