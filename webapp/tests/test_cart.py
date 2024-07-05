import pytest
from flask import url_for
from webapp.models import Product, CartItem


def test_add_to_cart_success(test_client, init_database, mocker):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/add_to_cart' page is posted to (POST)
    THEN check if the product is added to the cart successfully
    """
    mock_get_product = mocker.patch('webapp.services.ProductService.get', return_value=Product(
        product_id=1,
        name='Test Product',
        price=10.0,
        quantity=100
    ))

    mock_create_cart_item = mocker.patch('webapp.services.CartItemService.create', return_value=CartItem(
        cart_item_id=1,
        product_id=1,
        quantity=1,
        price=10.0
    ))

    response = test_client.post(url_for('main.add_to_cart', product_id=1), data=dict(
        quantity=1
    ), follow_redirects=True)

    assert response.status_code == 200
    assert b'Product added to cart successfully' in response.data
    mock_get_product.assert_called_once_with(1)
    mock_create_cart_item.assert_called_once_with(cart_id=1, product_id=1, quantity=1, price=10.0)


def test_add_to_cart_product_not_found(test_client, init_database, mocker):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/add_to_cart' page is posted to with a non-existent product (POST)
    THEN check if the appropriate error message is returned
    """
    mock_get_product = mocker.patch('webapp.services.ProductService.get', return_value=None)

    response = test_client.post(url_for('main.add_to_cart', product_id=1), data=dict(
        quantity=1
    ), follow_redirects=True)

    assert response.status_code == 200
    assert b'Product not found' in response.data
    mock_get_product.assert_called_once_with(1)
