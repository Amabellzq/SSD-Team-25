from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'User'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    profile_pic_url = db.Column(db.LargeBinary)
    role = db.Column(db.Enum('Admin', 'Merchant', 'Customer'), nullable=False)
    account_status = db.Column(db.Enum('Active', 'Inactive', 'Suspended'), nullable=False, default='Active')
    active_session_token = db.Column(db.String(255), nullable=True)
    shopping_cart = db.relationship('ShoppingCart', backref='user', uselist=False)
    orders = db.relationship('Order', backref='user')
    merchant = db.relationship('Merchant', backref='user', uselist=False)
    administrator = db.relationship('Administrator', backref='user', uselist=False)
    totp_secret = db.Column(db.String(64), nullable=True)  # Added field for TOTP secret

    def get_id(self):
        return str(self.user_id)

class Administrator(db.Model):
    __tablename__ = 'Administrator'
    admin_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'))

class Merchant(db.Model):
    __tablename__ = 'Merchant'
    merchant_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'))
    business_name = db.Column(db.String(255))
    business_address = db.Column(db.String(255))
    account_status = db.Column(db.Enum('Active', 'Inactive'))
    approved_date = db.Column(db.DateTime, default=datetime.utcnow)
    products = db.relationship('Product', backref='merchant')

class ShoppingCart(db.Model):
    __tablename__ = 'ShoppingCart'
    cart_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated_date = db.Column(db.DateTime)
    cart_items = db.relationship('CartItem', backref='shoppingcart')

class CartItem(db.Model):
    __tablename__ = 'CartItem'
    cart_item_id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('ShoppingCart.cart_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('Product.product_id'))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Numeric(10, 2))
    product = db.relationship('Product', backref=db.backref('cart_items', lazy=True))

class Product(db.Model):
    __tablename__ = 'Product'
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('Category.category_id'))
    price = db.Column(db.Numeric(10, 2))
    quantity = db.Column(db.Integer)
    availability = db.Column(db.Enum('In Stock', 'Out of Stock'))
    image_url = db.Column(db.LargeBinary, nullable=True)
    merchant_id = db.Column(db.Integer, db.ForeignKey('Merchant.merchant_id'))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated_date = db.Column(db.DateTime)

class Category(db.Model):
    __tablename__ = 'Category'
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    products = db.relationship('Product', backref='category')

class Order(db.Model):
    __tablename__ = 'Order'
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'))
    total_price = db.Column(db.Numeric(10, 2))
    collection_status = db.Column(db.Enum('Not Collected', 'Collected'))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated_date = db.Column(db.DateTime)
    order_items = db.relationship('OrderItem', backref='order')
    payment = db.relationship('Payment', backref='order', uselist=False)

class OrderItem(db.Model):
    __tablename__ = 'OrderItem'
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('Order.order_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('Product.product_id'))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Numeric(10, 2))
    merchant_id = db.Column(db.Integer, db.ForeignKey('Merchant.merchant_id'))  # Add this line

    product = db.relationship('Product', backref=db.backref('order_items', lazy=True))
    merchant = db.relationship('Merchant', backref=db.backref('order_items', lazy=True))
    

class Payment(db.Model):
    __tablename__ = 'Payment'
    payment_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('Order.order_id'))
    payment_method = db.Column(db.Enum('Credit Card', 'Debit Card'))
    amount = db.Column(db.Numeric(10, 2))
    payment_status = db.Column(db.Enum('Pending', 'Completed', 'Failed'))
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
