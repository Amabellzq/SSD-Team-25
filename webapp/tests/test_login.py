import pytest
from flask import url_for
from werkzeug.security import generate_password_hash
from webapp.model import User
def test_register_success(test_client, mocker):
    mocker.patch('webapp.services.UserService.create', return_value=True)
    response = test_client.post('/register', data=dict(username='testuser', email='newuser@example.com', password='testpassword'), follow_redirects=True)
    assert response.status_code == 200
    assert b'Registration successful' in response.data

def test_login_success(test_client, mocker):
    mocker.patch('webapp.services.UserService.get_by_username', return_value=User(username='testuser', password=generate_password_hash('testpassword')))
    mocker.patch('webapp.services.UserService.check_password', return_value=True)
    response = test_client.post('/login', data=dict(username='testuser', password='testpassword'), follow_redirects=True)
    assert response.status_code == 200
    assert b'Logout' in response.data

def test_login_invalid_credentials(test_client, mocker):
    mock_get_user = mocker.patch('webapp.services.UserService.get_by_username', return_value=None)
    response = test_client.post(url_for('main.login'), data=dict(username='testuser', password='wrongpassword'), follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data
    mock_get_user.assert_called_once_with('testuser')


def test_add_to_cart_product_not_found(test_client, mocker):
    mock_get_product = mocker.patch('webapp.services.ProductService.get', return_value=None)
    response = test_client.post(url_for('main.add_to_cart', product_id=1), data=dict(quantity=1), follow_redirects=True)
    assert response.status_code == 200
    assert b'Product not found' in response.data
    mock_get_product.assert_called_once_with(1)

@pytest.fixture(autouse=True)
def run_around_tests():
    # Setup before each test
    yield
    # Teardown after each test
    db.session.remove()