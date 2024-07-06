import pytest
from flask import url_for
from webapp.model import Product, CartItem
from webapp.services import UserService
from werkzeug.security import generate_password_hash
from webapp.model import User

def test_add_to_cart_success(test_client, init_database, mocker):
    mocker.patch('webapp.services.CartItemService.create', return_value=True)
    response = test_client.post('/add_to_cart', data=dict(product_id=1, quantity=1))
    assert response.status_code == 200
    assert b'Item added to cart' in response.data

def test_add_to_cart_product_not_found(test_client, init_database, mocker):
    mock_get_product = mocker.patch('webapp.services.ProductService.get', return_value=None)
    response = test_client.post(url_for('main.add_to_cart', product_id=1), data=dict(quantity=1), follow_redirects=True)
    assert response.status_code == 200
    assert b'Product not found' in response.data
    mock_get_product.assert_called_once_with(1)

def test_login_success(test_client, init_database, mocker):
    mocker.patch('webapp.services.UserService.get_by_username', return_value=User(username='testuser', password=generate_password_hash('testpassword')))
    mocker.patch('webapp.services.UserService.check_password', return_value=True)
    response = test_client.post('/login', data=dict(username='testuser', password='testpassword'), follow_redirects=True)
    assert response.status_code == 200
    assert b'Logout' in response.data

def test_register_success(test_client, init_database, mocker):
    mocker.patch('webapp.services.UserService.create', return_value=True)
    response = test_client.post('/register', data=dict(username='newuser', email='newuser@example.com', password='password'), follow_redirects=True)
    assert response.status_code == 200
    assert b'Registration successful' in response.data
