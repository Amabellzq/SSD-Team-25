import secrets
from flask import Blueprint, current_app, render_template, jsonify, redirect, url_for, flash, request, session, abort
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from .templates.includes.forms import LoginForm, RegistrationForm, CheckoutForm, AccountDetailsForm, CreateCategory, EditUserForm, UpdateProductForm, RegisterBusinessForm, CreateProductForm
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import base64
from datetime import datetime, timedelta
from .model import db, User, Category, Merchant, Order, Product, ShoppingCart, CartItem, OrderItem, Payment
from .services import UserService, CategoryService, MerchantService, OrderService, ProductService, ShoppingCartService, CartItemService, PaymentService, AdministratorService
import pyotp
import qrcode
from io import BytesIO
from PIL import Image
from functools import wraps

main = Blueprint('main', __name__)
login_manager = LoginManager()
login_manager.init_app(main)
login_manager.login_view = 'main.login'

def session_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = current_user
        if user.is_authenticated:
            if user.active_session_token != session.sid:
                logout_user()
                session.clear()
                return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    return UserService.get(user_id)

@main.route('/')
def home():
    categories = CategoryService.get_all()
    products = ProductService.get_all()

    unique_categories = {}
    categorized_products = {}
    for category in categories:
        if category.name not in unique_categories:
            unique_categories[category.name] = category
            categorized_products[category.name] = []

    for product in products:
        if product.category.name in categorized_products:
            categorized_products[product.category.name].append(product)
        else:
            categorized_products[product.category.name] = [product]

    return render_template('index.html', categories=unique_categories.values(), categorized_products=categorized_products)

@main.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('query')
    if not query:
        return redirect(url_for('main.home'))

    # Perform search in Product and Category tables
    products = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
    categories = Category.query.filter(Category.name.ilike(f'%{query}%')).all()

    return render_template('search_results.html', query=query, products=products, categories=categories)

@main.route('/shop', methods=['GET'])
def shop():
    page = request.args.get('page', 1, type=int)
    per_page = 6  # Number of products per page
    category_name = request.args.get('category', 'all')

    categories = CategoryService.get_all()
    # # products = ProductService.get_all()
    # products_pagination = Product.query.paginate(page=page, per_page=per_page)

    if category_name == 'all':
        pagination = Product.query.paginate(page=page, per_page=per_page)
    else:
        category = Category.query.filter_by(name=category_name).first_or_404()
        pagination = Product.query.filter_by(category_id=category.category_id).paginate(page=page, per_page=per_page)

    products = pagination.items

    unique_categories = {}
    categorized_products = {}
    for category in categories:
        if category.name not in unique_categories:
            unique_categories[category.name] = category
            categorized_products[category.name] = []

    for product in products:
        if product.category.name in categorized_products:
            categorized_products[product.category.name].append(product)
        else:
            categorized_products[product.category.name] = [product]

    return render_template('shop.html', categories=unique_categories.values(), categorized_products=categorized_products,
                            pagination=pagination, selected_category = category_name)

@main.route('/contact')
def contact():
    return render_template('contact.html')

@main.route('/productDetails/<int:product_id>')
def productDetails(product_id):
    product = ProductService.get(product_id)
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('main.shop'))
    
    related_products = ProductService.get_related_products(product.category_id, product_id)

    return render_template('product-details.html', product=product, related_products=related_products)

@main.route('/myprofile', methods=['GET', 'POST'])
@login_required
@session_required
def myaccount():
    user_id = current_user.user_id
    account_details_form = AccountDetailsForm()
    profile_pic_url = None

    if request.method == 'GET':
        user = UserService.get(user_id)
        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('main.myaccount'))

        account_details_form.username.data = user.username
        account_details_form.email.data = user.email
        account_details_form.role.data = user.role
        account_details_form.account_status.data = user.account_status
        if user.profile_pic_url:
            profile_pic_url = base64.b64encode(user.profile_pic_url).decode('utf-8')

    if request.method == 'POST' and account_details_form.validate_on_submit():
        user = UserService.get(user_id)
        if user:
            UserService.update(user_id, 
                username=account_details_form.username.data,
                email=account_details_form.email.data,
                password=generate_password_hash(account_details_form.password.data) if account_details_form.password.data else None,
                profile_pic_url=account_details_form.profile_picture.data.read() if account_details_form.profile_picture.data else None
            )
            flash('User updated successfully!', 'success')
            return redirect(url_for('main.myaccount'))
        else:
            flash('User not found', 'danger')

    return render_template('account.html', accountDetails=account_details_form, profile_pic_url=profile_pic_url, user=user)

@main.route('/add_to_cart', methods=['POST'])
@login_required
@session_required
def add_to_cart():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))
    user_id = current_user.user_id

    # Get the user's current shopping cart
    cart = ShoppingCart.query.filter_by(user_id=user_id).first()
    if not cart:
        cart = ShoppingCart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()

    # Check if the product is already in the cart
    cart_item = CartItem.query.filter_by(cart_id=cart.cart_id, product_id=product_id).first()
    if cart_item:
        # Update the quantity if the product is already in the cart
        cart_item.quantity += quantity
        cart_item.price = Product.query.get(product_id).price * cart_item.quantity
    else:
        # Add a new product to the cart
        product = Product.query.get(product_id)
        if not product:
            abort(404, description="Product not found")
        cart_item = CartItem(cart_id=cart.cart_id, product_id=product_id, quantity=quantity, price=product.price * quantity)
        db.session.add(cart_item)

    cart.last_updated_date = datetime.utcnow() + timedelta(hours=8)
    db.session.commit()
    flash('Product added to cart successfully!', 'success')
    return redirect(url_for('main.cart'))

@main.route('/cart')
@login_required
@session_required
def cart():
    user_id = current_user.user_id
    cart = ShoppingCart.query.filter_by(user_id=user_id).first()
    if not cart or not cart.cart_items:
        return render_template('cart.html', cart_items=[], total=0)

    cart_items = cart.cart_items
    total = sum(item.price for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)


@main.route('/remove_from_cart/<int:cart_item_id>')
@login_required
@session_required
def remove_from_cart(cart_item_id):
    try:
        cart_item = CartItem.query.get_or_404(cart_item_id)
        if cart_item.shoppingcart.user_id != current_user.id:
            abort(403)
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from cart', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {e}', 'danger')
    return redirect(url_for('main.cart'))

@main.route('/update_cart/<int:cart_item_id>', methods=['POST'])
@login_required
@session_required
def update_cart(cart_item_id):
    try:
        new_quantity = int(request.form.get('quantity', 1))
        cart_item = CartItem.query.get_or_404(cart_item_id)
        
        if cart_item.shoppingcart.user_id != current_user.user_id:
            abort(403)
        
        product_price = cart_item.product.price
        cart_item.quantity = new_quantity
        cart_item.price = product_price * new_quantity
        
        db.session.commit()
        flash('Cart updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {e}', 'danger')
    
    return redirect(url_for('main.cart'))



@main.route('/checkoutpage', methods=['GET', 'POST'])
@login_required
@session_required
def checkout():
    form = CheckoutForm()
    if form.validate_on_submit():
        # Process the order here
        return redirect(url_for('main.order_confirmation'))
    return render_template('checkout.html', checkout_form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        print('Form submitted')  # Debug statement
    if form.validate_on_submit():
        print('Form validated successfully')  # Debug statement
        username = form.username.data
        password = form.password.data
        print(f'Attempting to log in user: {username}')  # Debug statement

        user = UserService.get_by_username(username)
        
        if user:
            print(f'User found: {user.username}')  # Debug statement
        else:
            print(f'User not found: {username}')  # Debug statement

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.get_id()
            return redirect(url_for('main.totp'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)
            
            # totp = pyotp.TOTP(user.totp_secret)
            # if totp.verify(totp_code):
            #     login_user(user)  # Log the user in if TOTP is verified
            #     print(f'Login successful for user: {user.username}')  # Debug statement
            #     session['user_id'] = user.get_id()  # Store user ID in session
            #     print(f"Session started with user_id: {session.get('user_id')}")  # Debug statement
            #     return redirect(url_for('main.home'))
            # else:
            #     flash('Invalid TOTP code', 'danger')  # Show error if TOTP code is invalid
            #     print('Invalid TOTP code')  # Debug statement
                
            # # Redirect based on role
            # if user.role == 'Admin':
            #     print('Redirecting to admin dashboard')  # Debug statement
            #     return redirect(url_for('main.adminDashboard'))
            # elif user.role == 'Merchant':
            #     print('Redirecting to seller dashboard')  # Debug statement
            #     return redirect(url_for('main.sellerDashboard'))
            # else:
            #     print('Redirecting to home page')  # Debug statement
            #     return redirect(url_for('main.home'))
    #     else:
    #         flash('Invalid username or password', 'danger')
    #         print('Invalid username or password')  # Debug statement
    # else:
    #     if request.method == 'POST':
    #         print('Form validation failed')  # Debug statement
    #     else:
    #         print('GET request')  # Debug statement

    # return render_template('login.html', login_form=form)
    
    
# Route to generate TOTP QR code and verify TOTP code
@main.route('/totp', methods=['GET', 'POST'])
def totp():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('main.login'))

    user = UserService.get(user_id)
    if not user.totp_secret:
        user.totp_secret = pyotp.random_base32()
        db.session.commit()

    otp_uri = pyotp.totp.TOTP(user.totp_secret).provisioning_uri(user.email, issuer_name="YourAppName")
    img = qrcode.make(otp_uri,box_size=8,border=3)
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.getvalue()).decode('ascii')

    if request.method == 'POST':
        totp_code = request.form['totp']
        totp = pyotp.TOTP(user.totp_secret)
        if totp.verify(totp_code):
            # Invalidate previous session by setting a new session token
            session.clear()  # Clear any existing session data
            login_user(user)
            print(f'Login successful for user: {user.username}')  # Debug statement
            session['user_id'] = user.get_id()  # Store user ID in session
            user.active_session_token = session.sid  # Use Flask-Session's session ID
            db.session.commit()
            print(f"Session started with user_id: {session.get('user_id')} and session ID: {session.sid}")  # Debug statement
            # Check user role and merchant ID
            if user.role == 'Merchant':
                merchant = Merchant.query.filter_by(user_id=user.user_id).first()
                if merchant:
                    print(f'Merchant found: {merchant.merchant_id}')  # Debug statement
                    return redirect(url_for('main.sellerDashboard'))
                else:
                    print('No merchant found for the current user.')  # Debug statement
                    return redirect(url_for('main.register_business'))
            return redirect(url_for('main.home'))
        else:
            flash('Invalid username or password', 'danger')
            print('Invalid username or password')  # Debug statement
    else:
        if request.method == 'POST':
            print('Form validation failed')  # Debug statement
        else:
            flash('Invalid TOTP code', 'danger')

    return render_template('totp.html', img_b64=img_b64)


@main.route('/logout')
def logout():
    user = current_user
    if user.is_authenticated:
        user.active_session_token = None
        db.session.commit()
    logout_user()
    session.clear()  # Clear the session
    return redirect(url_for('main.home'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    registration_successful = False
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        role = form.role.data
        password = form.password.data
        profile_picture = form.profile_picture.data

        # Check for duplicate username
        existing_user = UserService.get_by_username(username)
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'danger')
        else:
            # Check for duplicate email
            existing_email = UserService.get_by_email(email)
            if existing_email:
                flash('Email already exists.', 'danger')
            else:
                hashed_password = generate_password_hash(password)
                try:
                    # Create the new user
                    new_user = UserService.create(username=username, email=email, password=hashed_password, role=role)
                    registration_successful = True
                    flash('Registration Successful', 'success')
                    return redirect(url_for('main.login'))
                except Exception as e:
                    db.session.rollback()
                    current_app.logger.error(f'Error while registering user: {str(e)}')
                    flash(f'An error occurred: {str(e)}', 'danger')
    else:
        if request.method == 'POST':
            current_app.logger.debug('Form validation failed')
            for field_name, errors in form.errors.items():
                field = getattr(form, field_name)
                for error in errors:
                    flash(f'{field.label.text}: {error}', 'danger')

    return render_template('register.html', register_form=form, registration_successful=registration_successful)

@main.route('/forgetPW', methods=['GET', 'POST'])
def forgetPass():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash('Please check your email')
        return redirect(url_for('main.login'))
    return render_template('forgetPW.html', resetpass_form=form)

#############################
# Admin #
#############################

@main.route('/adminDashboard', methods=['GET', 'POST'])
@login_required
def adminDashboard():
    user_id = current_user.user_id
    users = UserService.get_all()
    merchants = MerchantService.get_all()
    categories = CategoryService.get_all()
    accountDetails = AccountDetailsForm() 
    profile_pic_url = None

    user = UserService.get(user_id)
    if not user:
        return redirect(url_for('main.adminDashboard'))

    accountDetails.username.data = user.username
    accountDetails.role.data = user.role
    accountDetails.email.data = user.email
    accountDetails.account_status.data = user.account_status
    if user.profile_pic_url:
        profile_pic_url = base64.b64encode(user.profile_pic_url).decode('utf-8')

    return render_template('adminDashboard.html', users=users, categories=categories, merchants=merchants,
                           profile_pic_url=profile_pic_url, user=user, accountDetails=accountDetails)

@main.route('/updateAdmin_account', methods=['POST'])
@login_required
def updateAdmin_account():
    user_id = current_user.user_id
    account_details_form = AccountDetailsForm()
    if account_details_form.validate_on_submit():
        UserService.update(
            user_id,
            username=account_details_form.username.data,
            email=account_details_form.email.data,
            password=generate_password_hash(account_details_form.password.data) if account_details_form.password.data else None,
            profile_pic_url=account_details_form.profile_picture.data.read() if account_details_form.profile_picture.data else None
        )
    return redirect(url_for('main.adminDashboard'))

@main.route('/registerAdmin', methods=['GET', 'POST'])
def registerAdmin():
    form = RegistrationForm()
    registration_successful = False
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        role = 'Admin'  # Set role to 'Admin' explicitly
        password = form.password.data
        profile_picture = form.profile_picture.data

        # Check for duplicate username
        existing_user = UserService.get_by_username(username)
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'danger')
        else:
            hashed_password = generate_password_hash(password)
            try:
                # Create the new user
                new_user = UserService.create(username=username, email=email, password=hashed_password, role=role)
                if profile_picture:
                    new_user.profile_pic_url = profile_picture.read()
                db.session.commit()
                registration_successful = True
                return redirect(url_for('main.adminDashboard'))
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f'Error while registering user: {str(e)}')
    else:
        if request.method == 'POST':
            current_app.logger.debug('Form validation failed')
            for field, errors in form.errors.items():
                for error in errors:
                    current_app.logger.debug(f'{field}: {error}')

    return render_template('adminRegister.html', register_form=form, registration_successful=registration_successful)

@main.route('/editUser/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    form = EditUserForm()
    user = UserService.get(user_id)

    if not user:
        return redirect(url_for('main.adminDashboard'))

    if request.method == 'GET':
        form.username.data = user.username
        form.role.data = user.role
        form.account_status.data = user.account_status
        profile_pic_url = None
        if user.profile_pic_url:
            profile_pic_url = base64.b64encode(user.profile_pic_url).decode('utf-8')

    if request.method == 'POST' and form.validate_on_submit():
        UserService.update(
            user_id,
            account_status=form.account_status.data
        )
        return redirect(url_for('main.adminDashboard'))

    return render_template('adminManageUser.html', form=form, profile_pic_url=profile_pic_url, user=user)

@main.route('/deleteUser/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    UserService.delete(user_id)
    return redirect(url_for('main.adminDashboard'))

@main.route('/approve_merchant/<int:merchant_id>', methods=['POST'])
@login_required
def approve_merchant(merchant_id):
    MerchantService.update(
        merchant_id,
        account_status='Active',
        approved_date=datetime.utcnow() + timedelta(hours=8)
    )
    return redirect(url_for('main.adminDashboard'))

@main.route('/suspend_merchant/<int:merchant_id>', methods=['POST'])
def suspend_merchant(merchant_id):
    MerchantService.update(
        merchant_id,
        account_status='Inactive',
        approved_date=datetime.utcnow() + timedelta(hours=8)
    )
    return redirect(url_for('main.adminDashboard'))

@main.route('/createCategory', methods=['GET', 'POST'])
@login_required
def adminCreateCategory():
    create_category = CreateCategory()
    if create_category.validate_on_submit():
        CategoryService.create(
            name=create_category.categoryName.data,
            description=create_category.categoryDescription.data
        )
        return redirect(url_for('main.adminDashboard'))
    return render_template('adminCreateCategory.html', createNewCategory=create_category)

@main.route('/delete_category/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    CategoryService.delete(category_id)
    return redirect(url_for('main.adminDashboard'))

@main.route('/editCategory/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    form = CreateCategory()
    category = CategoryService.get(category_id)

    if not category:
        flash('Category not found', 'danger')
        return redirect(url_for('main.adminDashboard'))

    if request.method == 'GET':
        form.categoryName.data = category.name
        form.categoryDescription.data = category.description

    if request.method == 'POST' and form.validate_on_submit():
        CategoryService.update(
            category_id,
            name=form.categoryName.data,
            description=form.categoryDescription.data
        )
        flash('Category updated successfully!', 'success')
        return redirect(url_for('main.adminDashboard'))

    return render_template('adminEditCategory.html', form=form, category_id=category_id)

#############################
# Merchant #
#############################

@main.route('/sellerDashboard', methods=['GET'])
@login_required
def sellerDashboard():
    user_id = current_user.user_id
    account_details_form = AccountDetailsForm()
    update_business_form = RegisterBusinessForm()
    profile_pic_url = None

    user = UserService.get(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('main.sellerDashboard'))

    account_details_form.username.data = user.username
    account_details_form.email.data = user.email
    account_details_form.role.data = user.role
    account_details_form.account_status.data = user.account_status
    if user.profile_pic_url:
        profile_pic_url = base64.b64encode(user.profile_pic_url).decode('utf-8')

    merchant = MerchantService.get_by_user_id(user_id)
    if merchant:
        update_business_form.business_name.data = merchant.business_name
        update_business_form.business_address.data = merchant.business_address
        update_business_form.user_id.data = user_id

    orders = OrderService.get_all()
    products = ProductService.get_by_merchant_id(merchant.merchant_id)
    for product in products:
        if product.image_url:
            product.image_url = base64.b64encode(product.image_url).decode('utf-8')

    return render_template('sellerDashboard.html', accountDetails=account_details_form, updateBusiness=update_business_form, profile_pic_url=profile_pic_url, user=user, orders=orders, products=products)

@main.route('/update_account', methods=['POST'])
@login_required
def update_account():
    user_id = current_user.user_id
    account_details_form = AccountDetailsForm()
    if account_details_form.validate_on_submit():
        UserService.update(
            user_id,
            username=account_details_form.username.data,
            email=account_details_form.email.data,
            password=generate_password_hash(account_details_form.password.data) if account_details_form.password.data else None,
            profile_pic_url=account_details_form.profile_picture.data.read() if account_details_form.profile_picture.data else None
        )
    return redirect(url_for('main.sellerDashboard'))

@main.route('/register_business', methods=['GET', 'POST'])
@login_required
def register_business():
    user_id = current_user.user_id
    update_business_form = RegisterBusinessForm()

    current_app.logger.debug(f"Form data received: {request.form}")
    current_app.logger.debug(f"Form validation status: {update_business_form.validate_on_submit()}")

    if request.method == 'POST':
        if update_business_form.validate_on_submit():
            try:
                merchant = MerchantService.get_by_user_id(user_id)
                if merchant:
                    MerchantService.update(
                        merchant.merchant_id,
                        business_name=update_business_form.business_name.data,
                        business_address=update_business_form.business_address.data
                    )
                    current_app.logger.debug("Merchant details updated successfully!")
                else:
                    MerchantService.create(
                        user_id=user_id,
                        business_name=update_business_form.business_name.data,
                        business_address=update_business_form.business_address.data,
                        account_status='Inactive'
                    )
                    current_app.logger.debug("Merchant created successfully!")
                return redirect(url_for('main.sellerDashboard'))
            except Exception as e:
                current_app.logger.error(f"Error updating business details: {str(e)}")
                db.session.rollback()
                flash('An error occurred while updating business details.', 'danger')
        else:
            current_app.logger.debug("Form did not validate.")
            for field, errors in update_business_form.errors.items():
                for error in errors:
                    current_app.logger.debug(f"Error in {field}: {error}")

    merchant = MerchantService.get_by_user_id(user_id)
    if merchant:
        update_business_form.business_name.data = merchant.business_name
        update_business_form.business_address.data = merchant.business_address

    update_business_form.user_id.data = user_id
    return render_template('sellerRegBusiness.html', updateBusiness=update_business_form)

@main.route('/update_business', methods=['POST'])
@login_required
def update_business():
    user_id = current_user.user_id
    update_business_form = RegisterBusinessForm()

    if update_business_form.validate_on_submit():
        try:
            merchant = MerchantService.get_by_user_id(user_id)
            if merchant:
                MerchantService.update(
                    merchant.merchant_id,
                    business_name=update_business_form.business_name.data,
                    business_address=update_business_form.business_address.data
                )
                current_app.logger.debug("Merchant details updated successfully!")
                return redirect(url_for('main.sellerDashboard'))
        except Exception as e:
            current_app.logger.error(f"Error updating business details: {str(e)}")
            db.session.rollback()
            flash('An error occurred while updating business details.', 'danger')
    else:
        for field, errors in update_business_form.errors.items():
            for error in errors:
                current_app.logger.debug(f"Error in {field}: {error}")

    return render_template('sellerDashboard.html', updateBusiness=update_business_form)

@main.route('/orderDetails')
@login_required
def orderDetails():
    return render_template('sellerOrderDetails.html', user=current_user)

@main.route('/newProduct', methods=['GET', 'POST'])
@login_required
def newProduct():
    form = CreateProductForm()
    categories = CategoryService.get_all()
    unique_categories = {c.name: c.category_id for c in categories}
    form.productCategoryID.choices = [(category_id, name) for name, category_id in unique_categories.items()]

    merchant = MerchantService.get_by_user_id(current_user.user_id)
    if not merchant:
        flash('No merchant found for the current user.', 'danger')
        return redirect(url_for('main.sellerDashboard'))
    form.merchant_id.data = merchant.merchant_id

    if request.method == 'POST':
        if form.validate_on_submit():
            product_data = {
                "name": form.productName.data,
                "description": form.productDescription.data,
                "category_id": form.productCategoryID.data,
                "price": form.productPrice.data,
                "quantity": form.productQuantity.data,
                "availability": form.availability.data,
                "image_url": form.image_url.data.read() if form.image_url.data else None,
                "merchant_id": merchant.merchant_id,
                "created_date": datetime.utcnow() + timedelta(hours=8),
                "last_updated_date": datetime.utcnow() + timedelta(hours=8)
            }
            ProductService.create(**product_data)
            flash('Product created successfully!', 'success')
            return redirect(url_for('main.sellerDashboard'))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    current_app.logger.debug(f"Error in {field}: {error}")
    return render_template('sellerNewProduct.html', form=form)

@main.route('/updateProduct/<int:product_id>', methods=['GET', 'POST'])
@login_required
def updateProduct(product_id):
    form = UpdateProductForm()
    product = ProductService.get(product_id)
    form.productCategoryID.choices = [(c.category_id, c.name) for c in CategoryService.get_all()]
    image_url = None

    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('main.sellerDashboard'))

    merchant = MerchantService.get_by_user_id(current_user.user_id)
    if not merchant:
        flash('No merchant found for the current user.', 'danger')
        return redirect(url_for('main.sellerDashboard'))
    form.merchant_id.data = merchant.merchant_id

    if request.method == 'GET':
        if product.image_url:
            image_url = base64.b64encode(product.image_url).decode('utf-8')
        form.productName.data = product.name
        form.productDescription.data = product.description
        form.productCategoryID.data = product.category_id
        form.productPrice.data = product.price
        form.productQuantity.data = product.quantity
        form.productCreatedDate.data = product.created_date
        form.productLastUpdated.data = product.last_updated_date

    if request.method == 'POST' and form.validate_on_submit():
        product_data = {
            "name": form.productName.data,
            "description": form.productDescription.data,
            "category_id": form.productCategoryID.data,
            "price": form.productPrice.data,
            "quantity": form.productQuantity.data,
            "availability": form.availability.data,
            "last_updated_date": datetime.utcnow() + timedelta(hours=8),
            "image_url": form.image_url.data.read() if form.image_url.data else product.image_url
        }
        ProductService.update(product_id, **product_data)
        flash('Product updated successfully!', 'success')
        return redirect(url_for('main.sellerDashboard'))

    if request.method == 'POST' and not form.validate_on_submit():
        current_app.logger.debug("Form validation failed")
        current_app.logger.debug(form.errors)

    return render_template('sellerUpdateProduct.html', form=form, image_url=image_url, product_id=product_id)

@main.route('/deleteProduct/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    ProductService.delete(product_id)
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('main.sellerDashboard'))

@main.route('/session-info')
def session_info():
    user_id = session.get('user_id')
    if user_id:
        return f"Session active for user_id: {user_id}"
    else:
        return "No active session"
