from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db_admin, db_user, db_readonly

class User(UserMixin, db_user.Model):
    __tablename__ = 'user'
    user_id = db_user.Column(db_user.Integer, primary_key=True)
    username = db_user.Column(db_user.String(255), unique=True, nullable=False)
    password = db_user.Column(db_user.String(255), nullable=False)
    profile_pic_url = db_user.Column(db_user.MediumBlob)
    role = db_user.Column(db_user.Enum('Admin', 'Merchant', 'Customer'), nullable=False)
    account_status = db_user.Column(db_user.Enum('Active', 'Inactive', 'Suspended'), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Administrator(db_admin.Model):
    __tablename__ = 'administrator'
    admin_id = db_admin.Column(db_admin.Integer, primary_key=True)
    user_id = db_admin.Column(db_admin.Integer, db_admin.ForeignKey('user.user_id'), nullable=False)

class Merchant(db_user.Model):
    __tablename__ = 'merchant'
    merchant_id = db_user.Column(db_user.Integer, primary_key=True)
    user_id = db_user.Column(db_user.Integer, db_user.ForeignKey('user.user_id'), nullable=False)
    business_name = db_user.Column(db_user.String(255), nullable=False)
    business_address = db_user.Column(db_user.String(255), nullable=False)
    account_status = db_user.Column(db_user.Enum('Active', 'Inactive'), nullable=False)
    approved_date = db_user.Column(db_user.DateTime, nullable=False, default=datetime.utcnow)

class Session(db_user.Model):
    __tablename__ = 'session'
    session_id = db_user.Column(db_user.Integer, primary_key=True)
    user_id = db_user.Column(db_user.Integer, db_user.ForeignKey('user.user_id'), nullable=False)
    session_token = db_user.Column(db_user.String(255), unique=True, nullable=False)
    created_date = db_user.Column(db_user.DateTime, default=datetime.utcnow)
    expiry_date = db_user.Column(db_user.DateTime)
    last_activity_date = db_user.Column(db_user.DateTime, default=datetime.utcnow)
    is_active = db_user.Column(db_user.Boolean, default=True)

class Product(db_user.Model):
    __tablename__ = 'product'
    product_id = db_user.Column(db_user.Integer, primary_key=True)
    name = db_user.Column(db_user.String(255), nullable=False)
    description = db_user.Column(db_user.String(255), nullable=True)
    category_id = db_user.Column(db_user.Integer, db_user.ForeignKey('category.category_id'), nullable=False)
    price = db_user.Column(db_user.Numeric(10, 2), nullable=False)
    quantity = db_user.Column(db_user.Integer, nullable=False)
    availability = db_user.Column(db_user.Enum('In Stock', 'Out of Stock'), nullable=False)
    image_url = db_user.Column(db_user.MediumBlob, nullable=True)
    merchant_id = db_user.Column(db_user.Integer, db_user.ForeignKey('merchant.merchant_id'), nullable=False)
    created_date = db_user.Column(db_user.DateTime, default=datetime.utcnow)
    last_updated_date = db_user.Column(db_user.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Category(db_user.Model):
    __tablename__ = 'category'
    category_id = db_user.Column(db_user.Integer, primary_key=True)
    name = db_user.Column(db_user.String(255), nullable=False)
    description = db_user.Column(db_user.String(255), nullable=True)

class Order(db_user.Model):
    __tablename__ = 'order'
    order_id = db_user.Column(db_user.Integer, primary_key=True)
    user_id = db_user.Column(db_user.Integer, db_user.ForeignKey('user.user_id'), nullable=False)
    merchant_id = db_user.Column(db_user.Integer, db_user.ForeignKey('merchant.merchant_id'), nullable=False)
    total_price = db_user.Column(db_user.Numeric(10, 2), nullable=False)
    collection_status = db_user.Column(db_user.Enum('Not Collected', 'Collected'), nullable=False)
    created_date = db_user.Column(db_user.DateTime, default=datetime.utcnow)
    last_updated_date = db_user.Column(db_user.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class OrderItem(db_user.Model):
    __tablename__ = 'order_item'
    order_item_id = db_user.Column(db_user.Integer, primary_key=True)
    order_id = db_user.Column(db_user.Integer, db_user.ForeignKey('order.order_id'), nullable=False)
    product_id = db_user.Column(db_user.Integer, db_user.ForeignKey('product.product_id'), nullable=False)
    quantity = db_user.Column(db_user.Integer, nullable=False)
    price = db_user.Column(db_user.Numeric(10, 2), nullable=False)

class Payment(db_user.Model):
    __tablename__ = 'payment'
    payment_id = db_user.Column(db_user.Integer, primary_key=True)
    order_id = db_user.Column(db_user.Integer, db_user.ForeignKey('order.order_id'), nullable=False)
    payment_method = db_user.Column(db_user.Enum('Credit Card', 'Debit Card'), nullable=False)
    amount = db_user.Column(db_user.Numeric(10, 2), nullable=False)
    payment_status = db_user.Column(db_user.Enum('Pending', 'Completed', 'Failed'), nullable=False)
    transaction_date = db_user.Column(db_user.DateTime, default=datetime.utcnow)

class ShoppingCart(db_user.Model):
    __tablename__ = 'shopping_cart'
    cart_id = db_user.Column(db_user.Integer, primary_key=True)
    user_id = db_user.Column(db_user.Integer, db_user.ForeignKey('user.user_id'), nullable=False)
    created_date = db_user.Column(db_user.DateTime, default=datetime.utcnow)
    last_updated_date = db_user.Column(db_user.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CartItem(db_user.Model):
    __tablename__ = 'cart_item'
    cart_item_id = db_user.Column(db_user.Integer, primary_key=True)
    cart_id = db_user.Column(db_user.Integer, db_user.ForeignKey('shopping_cart.cart_id'), nullable=False)
    product_id = db_user.Column(db_user.Integer, db_user.ForeignKey('product.product_id'), nullable=False)
    quantity = db_user.Column(db_user.Integer, nullable=False)
    price = db_user.Column(db_user.Numeric(10, 2), nullable=False)
