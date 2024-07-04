from datetime import datetime, timedelta
from .model import db, User, Category, Merchant, Order, Product, ShoppingCart, CartItem, OrderItem, Payment

class UserService:
    
    @staticmethod
    def get(user_id):
        return User.query.get(user_id)

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def create(username, email, password, role):
        new_user = User(username=username, email=email, password=password, role=role, account_status='Active')
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @staticmethod
    def delete(user_id):
        user = UserService.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False

    @staticmethod
    def update(user_id, **kwargs):
        user = UserService.get(user_id)
        if user:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(user, key, value)
            db.session.commit()
            return user
        return None

    @staticmethod
    def get_all():
        return User.query.all()

class AdministratorService:
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
        admin = AdministratorService.get(admin_id)
        if admin:
            db.session.delete(admin)
            db.session.commit()
            return True
        return False

class MerchantService:
    @staticmethod
    def get(merchant_id):
        return Merchant.query.get(merchant_id)

    @staticmethod
    def get_by_user_id(user_id):
        return Merchant.query.filter_by(user_id=user_id).first()

    @staticmethod
    def create(user_id, business_name, business_address, account_status):
        current_time_utc_plus_8 = datetime.utcnow() + timedelta(hours=8)
        new_merchant = Merchant(
            user_id=user_id, 
            business_name=business_name, 
            business_address=business_address, 
            account_status=account_status,
            approved_date=current_time_utc_plus_8
        )
        db.session.add(new_merchant)
        db.session.commit()
        return new_merchant

    @staticmethod
    def delete(merchant_id):
        merchant = MerchantService.get(merchant_id)
        if merchant:
            db.session.delete(merchant)
            db.session.commit()
            return True
        return False

    @staticmethod
    def update(merchant_id, **kwargs):
        merchant = MerchantService.get(merchant_id)
        if merchant:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(merchant, key, value)
            db.session.commit()
            return merchant
        return None

    @staticmethod
    def get_all():
        return Merchant.query.all()

class ShoppingCartService:
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
        cart = ShoppingCartService.get(cart_id)
        if cart:
            db.session.delete(cart)
            db.session.commit()
            return True
        return False

    @staticmethod
    def update(cart_id, **kwargs):
        cart = ShoppingCartService.get(cart_id)
        if cart:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(cart, key, value)
            db.session.commit()
            return cart
        return None

class CartItemService:
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
        cart_item = CartItemService.get(cart_item_id)
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
            return True
        return False

    @staticmethod
    def update(cart_item_id, **kwargs):
        cart_item = CartItemService.get(cart_item_id)
        if cart_item:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(cart_item, key, value)
            db.session.commit()
            return cart_item
        return None

class ProductService:
    @staticmethod
    def get(product_id):
        return Product.query.get(product_id)

    @staticmethod
    def get_all():
        return Product.query.all()

    @staticmethod
    def get_by_merchant_id(merchant_id):
        return Product.query.filter_by(merchant_id=merchant_id).all()

    @staticmethod
    def create(name, description, category_id, price, quantity, availability, image_url, merchant_id, created_date, last_updated_date):
        new_product = Product(
            name=name,
            description=description,
            category_id=category_id,
            price=price,
            quantity=quantity,
            availability=availability,
            image_url=image_url,
            merchant_id=merchant_id,
            created_date=created_date,
            last_updated_date=last_updated_date
        )
        db.session.add(new_product)
        db.session.commit()
        return new_product

    @staticmethod
    def delete(product_id):
        product = ProductService.get(product_id)
        if product:
            db.session.delete(product)
            db.session.commit()
            return True
        return False

    @staticmethod
    def update(product_id, **kwargs):
        product = ProductService.get(product_id)
        if product:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(product, key, value)
            db.session.commit()
            return product
        return None

    @staticmethod
    def get_related_products(category_id, product_id):
        return Product.query.filter(Product.category_id == category_id, Product.product_id != product_id).all()

class CategoryService:
    @staticmethod
    def get(category_id):
        return Category.query.get(category_id)

    @staticmethod
    def get_all():
        return Category.query.all()

    @staticmethod
    def create(name, description):
        new_category = Category(name=name, description=description)
        db.session.add(new_category)
        db.session.commit()
        return new_category

    @staticmethod
    def delete(category_id):
        category = CategoryService.get(category_id)
        if category:
            db.session.delete(category)
            db.session.commit()
            return True
        return False

    @staticmethod
    def update(category_id, **kwargs):
        category = CategoryService.get(category_id)
        if category:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(category, key, value)
            db.session.commit()
            return category
        return None

class OrderService:
    @staticmethod
    def get(order_id):
        return Order.query.get(order_id)

    @staticmethod
    def get_all():
        return Order.query.all()

    @staticmethod
    def create(user_id, merchant_id, total_price, collection_status):
        new_order = Order(user_id=user_id, merchant_id=merchant_id, total_price=total_price, collection_status=collection_status)
        db.session.add(new_order)
        db.session.commit()
        return new_order

    @staticmethod
    def update(order_id, **kwargs):
        order = OrderService.get(order_id)
        if order:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(order, key, value)
            db.session.commit()
            return order
        return None

class OrderItemService:
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
        order_item = OrderItemService.get(order_item_id)
        if order_item:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(order_item, key, value)
            db.session.commit()
            return order_item
        return None

class PaymentService:
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
        payment = PaymentService.get(payment_id)
        if payment:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(payment, key, value)
            db.session.commit()
            return payment
        return None
