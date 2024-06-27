from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    profile_pic_url = db.Column(db.LargeBinary)
    role = db.Column(db.Enum('Admin', 'Merchant', 'Customer'), nullable=False)
    account_status = db.Column(db.Enum('Active', 'Inactive', 'Suspended'), nullable=False)
    shopping_cart = db.relationship('ShoppingCart', backref='user', uselist=False)
    orders = db.relationship('Order', backref='user')
    sessions = db.relationship('Session', backref='user')
    merchant = db.relationship('Merchant', backref='user', uselist=False)
    administrator = db.relationship('Administrator', backref='user', uselist=False)

    @staticmethod
    def get(user_id):
        return User.query.get(user_id)

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def create(username, password, role, account_status):
        new_user = User(username=username, password=password, role=role, account_status=account_status)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @staticmethod
    def delete(user_id):
        user = User.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False

    @staticmethod
    def update(user_id, **kwargs):
        user = User.get(user_id)
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            db.session.commit()
            return user
        return None

class Administrator(db.Model):
    __tablename__ = 'administrator'
    admin_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    @staticmethod
    def get(admin_id):
        return Administrator.query.get(admin_id)

    @staticmethod
    def create(user_id):
        new_admin = Administrator(user_id=user_id)
        db.session.add(new_admin)
        db.session.commit()
        return new_admin

    @staticmethod
    def delete(admin_id):
        admin = Administrator.get(admin_id)
        if admin:
            db.session.delete(admin)
            db.session.commit()
            return True
        return False

class Merchant(db.Model):
    __tablename__ = 'merchant'
    merchant_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    business_name = db.Column(db.String(255))
    business_address = db.Column(db.String(255))
    account_status = db.Column(db.Enum('Active', 'Inactive'))
    approved_date = db.Column(db.DateTime, default=datetime.utcnow)
    products = db.relationship('Product', backref='merchant')

    @staticmethod
    def get(merchant_id):
        return Merchant.query.get(merchant_id)

    @staticmethod
    def create(user_id, business_name, business_address, account_status):
        new_merchant = Merchant(user_id=user_id, business_name=business_name, business_address=business_address, account_status=account_status)
        db.session.add(new_merchant)
        db.session.commit()
        return new_merchant

    @staticmethod
    def delete(merchant_id):
        merchant = Merchant.get(merchant_id)
        if merchant:
            db.session.delete(merchant)
            db.session.commit()
            return True
        return False

    @staticmethod
    def update(merchant_id, **kwargs):
        merchant = Merchant.get(merchant_id)
        if merchant:
            for key, value in kwargs.items():
                setattr(merchant, key, value)
            db.session.commit()
            return merchant
        return None

class Session(db.Model):
    __tablename__ = 'session'
    session_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    session_token = db.Column(db.String(255))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime)
    last_activity_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    @staticmethod
    def get(session_id):
        return Session.query.get(session_id)

    @staticmethod
    def create(user_id, session_token, expiry_date, is_active=True):
        new_session = Session(user_id=user_id, session_token=session_token, expiry_date=expiry_date, is_active=is_active)
        db.session.add(new_session)
        db.session.commit()
        return new_session

    @staticmethod
    def delete(session_id):
        session = Session.get(session_id)
        if session:
            db.session.delete(session)
            db.session.commit()
            return True
        return False

    @staticmethod
    def update(session_id, **kwargs):
        session = Session.get(session_id)
        if session:
            for key, value in kwargs.items():
                setattr(session, key, value)
            db.session.commit()
            return session
        return None

class ShoppingCart(db.Model):
    __tablename__ = 'shoppingcart'
    cart_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated_date = db.Column(db.DateTime)
    cart_items = db.relationship('CartItem', backref='shoppingcart')

    @staticmethod
    def get(cart_id):
        return ShoppingCart.query.get(cart_id)

    @staticmethod
    def create(user_id):
        new_cart = ShoppingCart(user_id=user_id)
        db.session.add(new_cart)
        db.session.commit()
        return new_cart

    @staticmethod
    def delete(cart_id):
        cart = ShoppingCart.get(cart_id)
        if cart:
            db.session.delete(cart)
            db.session.commit()
            return True
        return False

    @staticmethod
    def update(cart_id, **kwargs):
        cart = ShoppingCart.get(cart_id)
        if cart:
            for key, value in kwargs.items():
                setattr(cart, key, value)
            db.session.commit()
            return cart
        return None

class CartItem(db.Model):
    __tablename__ = 'cartitem'
    cart_item_id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('shoppingcart.cart_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Numeric(10, 2))

    @staticmethod
    def get(cart_item_id):
        return CartItem.query.get(cart_item_id)

    @staticmethod
    def create(cart_id, product_id, quantity, price):
        new_cart_item = CartItem(cart_id=cart_id, product_id=product_id, quantity=quantity, price=price)
        db.session.add(new_cart_item)
        db.session.commit()
        return new_cart_item

    @staticmethod
    def delete(cart_item_id):
        cart_item = CartItem.get(cart_item_id)
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
            return True
        return False

    @staticmethod
    def update(cart_item_id, **kwargs):
        cart_item = CartItem.get(cart_item_id)
        if cart_item:
            for key, value in kwargs.items():
                setattr(cart_item, key, value)
            db.session.commit()
            return cart_item
        return None

class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'))
    price = db.Column(db.Numeric(10, 2))
    quantity = db.Column(db.Integer)
    availability = db.Column(db.Enum('In Stock', 'Out of Stock'))
    image_url = db.Column(db.LargeBinary)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchant.merchant_id'))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated_date = db.Column(db.DateTime)
    order_items = db.relationship('OrderItem', backref='product')
    cart_items = db.relationship('CartItem', backref='product')

    @staticmethod
    def get(product_id):
        return Product.query.get(product_id)

    @staticmethod
    def create(name, description, category_id, price, quantity, availability, image_url, merchant_id):
        new_product = Product(name=name, description=description, category_id=category_id, price=price, quantity=quantity, availability=availability, image_url=image_url, merchant_id=merchant_id)
        db.session.add(new_product)
        db.session.commit()
        return new_product

    @staticmethod
    def delete(product_id):
        product = Product.get(product_id)
        if product:
            db.session.delete(product)
            db.session.commit()
            return True
        return False

    @staticmethod
    def update(product_id, **kwargs):
        product = Product.get(product_id)
        if product:
            for key, value in kwargs.items():
                setattr(product, key, value)
            db.session.commit()
            return product
        return None

class Category(db.Model):
    __tablename__ = 'category'
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    products = db.relationship('Product', backref='category')

    @staticmethod
    def get(category_id):
        return Category.query.get(category_id)

    @staticmethod
    def create(name, description):
        new_category = Category(name=name, description=description)
        db.session.add(new_category)
        db.session.commit()
        return new_category

    @staticmethod
    def delete(category_id):
        category = Category.get(category_id)
        if category:
            db.session.delete(category)
            db.session.commit()
            return True
        return False

    @staticmethod
    def update(category_id, **kwargs):
        category = Category.get(category_id)
        if category:
            for key, value in kwargs.items():
                setattr(category, key, value)
            db.session.commit()
            return category
        return None

class Order(db.Model):
    __tablename__ = 'order'
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchant.merchant_id'))
    total_price = db.Column(db.Numeric(10, 2))
    collection_status = db.Column(db.Enum('Not Collected', 'Collected'))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated_date = db.Column(db.DateTime)
    order_items = db.relationship('OrderItem', backref='order')
    payment = db.relationship('Payment', backref='order', uselist=False)

    @staticmethod
    def get(order_id):
        return Order.query.get(order_id)

    @staticmethod
    def create(user_id, merchant_id, total_price, collection_status):
        new_order = Order(user_id=user_id, merchant_id=merchant_id, total_price=total_price, collection_status=collection_status)
        db.session.add(new_order)
        db.session.commit()
        return new_order

    @staticmethod
    def update(order_id, **kwargs):
        order = Order.get(order_id)
        if order:
            for key, value in kwargs.items():
                setattr(order, key, value)
            db.session.commit()
            return order
        return None

class OrderItem(db.Model):
    __tablename__ = 'orderitem'
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Numeric(10, 2))

    @staticmethod
    def get(order_item_id):
        return OrderItem.query.get(order_item_id)

    @staticmethod
    def create(order_id, product_id, quantity, price):
        new_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=quantity, price=price)
        db.session.add(new_order_item)
        db.session.commit()
        return new_order_item

    @staticmethod
    def update(order_item_id, **kwargs):
        order_item = OrderItem.get(order_item_id)
        if order_item:
            for key, value in kwargs.items():
                setattr(order_item, key, value)
            db.session.commit()
            return order_item
        return None

class Payment(db.Model):
    __tablename__ = 'payment'
    payment_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'))
    payment_method = db.Column(db.Enum('Credit Card', 'Debit Card'))
    amount = db.Column(db.Numeric(10, 2))
    payment_status = db.Column(db.Enum('Pending', 'Completed', 'Failed'))
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def get(payment_id):
        return Payment.query.get(payment_id)

    @staticmethod
    def create(order_id, payment_method, amount, payment_status):
        new_payment = Payment(order_id=order_id, payment_method=payment_method, amount=amount, payment_status=payment_status)
        db.session.add(new_payment)
        db.session.commit()
        return new_payment


    @staticmethod
    def update(payment_id, **kwargs):
        payment = Payment.get(payment_id)
        if payment:
            for key, value in kwargs.items():
                setattr(payment, key, value)
            db.session.commit()
            return payment
        return None
