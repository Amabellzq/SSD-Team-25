import secrets, requests
from flask import Blueprint, current_app, render_template, jsonify, redirect, url_for, flash, request, session
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from .templates.includes.forms import LoginForm, RegistrationForm, CheckoutForm, AccountDetailsForm, CreateCategory, EditUserForm, UpdateProductForm, RegisterBusinessForm, CreateProductForm
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import base64
from datetime import datetime, timedelta
from .models import db, User, Category, Merchant, Order, Product, ShoppingCart, CartItem, OrderItem, Payment
from functools import wraps

main = Blueprint('main', __name__)
login_manager = LoginManager()
login_manager.init_app(main)
login_manager.login_view = 'main.login'

def validate_recaptcha(recaptcha_response):
    data = {
        'secret': current_app.config['RECAPTCHA_PRIVATE_KEY'],
        'response': recaptcha_response
    }
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    result = r.json()
    print(f"reCAPTCHA API result: {result}")  # Debug statement
    if not result.get('success'):
        error_codes = result.get('error-codes', [])
        print(f"reCAPTCHA error codes: {error_codes}")  # Print error codes if validation fails
    return result.get('success')

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
    return User.get(user_id)


@main.route('/')
def home():
    categories = Category.query.all()
    products = Product.query.all()  # Query all products

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

    return render_template('index.html', categories = unique_categories.values(), categorized_products=categorized_products) #, products=products


# @main.route('/shop')
# def shop():
#     categories = Category.query.all()
#     products = Product.query.all()  # Query all products

#     unique_categories = {}
#     for category in categories:
#         if category.name not in unique_categories:
#             unique_categories[category.name] = {
#                 'descriptions': [],
#                 'products': []
#             }
#         unique_categories[category.name]['descriptions'].append(category.description)

#     for product in products:
#         category_name = product.category.name
#         if category_name in unique_categories:
#             unique_categories[category_name]['products'].append(product)
    
#     return render_template('shop.html', categories = unique_categories)

# @main.route('/shop')
# def shop():
#     categories = Category.query.all()
#     products = Product.query.all()  # Query all products

#     unique_categories = {}
#     categorized_products = {}
#     for category in categories:
#         if category.name not in unique_categories:
#             unique_categories[category.name] = category
#             categorized_products[category.name] = []

#     for product in products:
#         if product.category.name in categorized_products:
#             categorized_products[product.category.name].append(product)
#         else:
#             categorized_products[product.category.name] = [product]
    
#     return render_template('shop.html', categories = unique_categories.values(), categorized_products=categorized_products)

@main.route('/shop')
def shop():
    categories = Category.query.all()
    products = Product.query.all()  # Query all products

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

    return render_template('shop.html', categories=unique_categories.values(), categorized_products=categorized_products)


@main.route('/contact')
def contact():
    return render_template('contact.html')


@main.route('/productDetails')
def productDetails():
    return render_template('product-details.html')

@main.route('/myprofile', methods=['GET', 'POST'])
@login_required
@session_required
def myaccount():
    user_id = current_user.user_id
    account_details_form = AccountDetailsForm()
    profile_pic_url = None

    if request.method == 'GET':
        user = User.get(user_id)
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
        user = User.get(user_id)
        if user:
            user.username = account_details_form.username.data
            user.email = account_details_form.email.data
            if account_details_form.password.data:
                user.password = generate_password_hash(account_details_form.password.data)
            if account_details_form.profile_picture.data:
                profile_picture = account_details_form.profile_picture.data
                filename = secure_filename(profile_picture.filename)
                user.profile_pic_url = profile_picture.read()
            db.session.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('main.myaccount'))
        else:
            flash('User not found', 'danger')
    return render_template('account.html', accountDetails=account_details_form, profile_pic_url=profile_pic_url,
                           user=user)
    pass


@main.route('/cart')
@login_required
@session_required
def cart():
    return render_template('cart.html', user=current_user)


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
        user = User.get_by_username(username)
        if user:
            print(f'User found: {user.username}')  # Debug statement
        else:
            print(f'User not found: {username}')  # Debug statement
        if user and check_password_hash(user.password, password):
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
            print('GET request')  # Debug statement
    return render_template('login.html', login_form=form)


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
    recaptcha_public_key = current_app.config['RECAPTCHA_PUBLIC_KEY']
    
    if form.validate_on_submit():
        recaptcha_response = request.form.get('g-recaptcha-response')
        print(f"g-recaptcha-response: {recaptcha_response}")  # Debug statement
        if not validate_recaptcha(recaptcha_response):
            flash('Invalid reCAPTCHA. Please try again.', 'danger')
            print('Invalid reCAPTCHA')  # Debug statement
            return render_template('register.html', register_form=form, recaptcha_public_key=recaptcha_public_key)

    

        username = form.username.data
        email = form.email.data
        role = form.role.data
        password = form.password.data

        # Check for duplicate username
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'danger')
        else:
            # Check for duplicate email
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                flash('Email already exists.', 'danger')
            else:
                hashed_password = generate_password_hash(password)
                try:
                    # Create the new user
                    new_user = User.create(username=username, email=email, password=hashed_password, role=role)
                    registration_successful = True
                    flash('Registration Successful', 'success')
                    return redirect(url_for('main.login'))
                except Exception as e:
                    db.session.rollback()
                    current_app.logger.error(f'Error while registering user: {str(e)}')
                    flash(f'An error occurred: {str(e)}', 'danger')
    else:
        if request.method == 'POST':
            print('Form validation failed')  # Debug statement
            for field_name, errors in form.errors.items():
                field = getattr(form, field_name)
                for error in errors:
                    flash(f'{field.label.text}: {error}', 'danger')

    return render_template('register.html', register_form=form, recaptcha_public_key=recaptcha_public_key, registration_successful=registration_successful)

# def register():
#     form = RegistrationForm()
#     registration_successful = False
#     if form.validate_on_submit():
#         username = form.username.data
#         email = form.email.data
#         role = form.role.data
#         password = form.password.data
            


#         # Check for duplicate username
#         existing_user = User.query.filter_by(username=username).first()
#         if existing_user:
#             flash('Username already exists. Please choose a different username.', 'danger')
#         else:
#             # Check for duplicate email
#             existing_email = User.query.filter_by(email=email).first()
#             if (existing_email):
#                 flash('Email already exists.', 'danger')
#             else:
#                 hashed_password = generate_password_hash(password)
#                 try:
#                     # Create the new user
#                     new_user = User.create(username=username, email=email, password=hashed_password, role=role)

#                     registration_successful = True
#                     flash('Registration Successful', 'success')
#                     return redirect(url_for('main.login'))

#                 except Exception as e:
#                     db.session.rollback()
#                     current_app.logger.error(f'Error while registering user: {str(e)}')
#                     flash(f'An error occurred: {str(e)}', 'danger')
#     else:
#         if request.method == 'POST':
#             current_app.logger.debug('Form validation failed')
#             for field_name, errors in form.errors.items():
#                 field = getattr(form, field_name)
#                 for error in errors:
#                     flash(f'{field.label.text}: {error}', 'danger')

#     return render_template('register.html', register_form=form, registration_successful=registration_successful)


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
    users = User.query.all()
    merchants = Merchant.query.all()
    categories = Category.query.all()
    accountDetails = AccountDetailsForm() 
    profile_pic_url = None

    user = User.get(user_id)
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
        user = User.get(user_id)
        if user:
            user.username = account_details_form.username.data
            user.email = account_details_form.email.data
            if account_details_form.password.data:
                user.password = generate_password_hash(account_details_form.password.data)
            if account_details_form.profile_picture.data:
                profile_picture = account_details_form.profile_picture.data
                filename = secure_filename(profile_picture.filename)
                user.profile_pic_url = profile_picture.read()
            db.session.commit()

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
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'danger')
        else:
            hashed_password = generate_password_hash(password)
            try:
                # Create the new user
                new_user = User(username=username, email = email, password=hashed_password, role=role)

                if profile_picture:
                    filename = secure_filename(profile_picture.filename)
                    new_user.profile_pic_url = profile_picture.read()

                db.session.add(new_user)
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
    user = User.get(user_id)

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
        user.account_status = form.account_status.data
        db.session.commit()
        return redirect(url_for('main.adminDashboard'))

    return render_template('adminManageUser.html', form=form, profile_pic_url=profile_pic_url, user=user)


@main.route('/deleteUser/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()

    return redirect(url_for('main.adminDashboard'))


@main.route('/approve_merchant/<int:merchant_id>', methods=['POST'])
@login_required
def approve_merchant(merchant_id):
    merchant = Merchant.get(merchant_id)
    if merchant:
        merchant.account_status = 'Active'
        utc_now = datetime.utcnow()
        utc_plus_8 = utc_now + timedelta(hours=8)
        merchant.approved_date = utc_plus_8
        db.session.commit()

    return redirect(url_for('main.adminDashboard'))


@main.route('/suspend_merchant/<int:merchant_id>', methods=['POST'])
def suspend_merchant(merchant_id):
    merchant = Merchant.get(merchant_id)
    if merchant:
        try:
            merchant.account_status = 'Inactive'
            merchant.approved_date = datetime.utcnow() + timedelta(hours=8)  # Adjust to UTC+8
            db.session.commit()
            flash('Merchant suspended successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error suspending merchant: {str(e)}')
            flash('An error occurred while suspending the merchant.', 'danger')
    else:
        flash('Merchant not found.', 'danger')
    return redirect(url_for('main.adminDashboard'))


@main.route('/createCategory', methods=['GET', 'POST'])
@login_required
def adminCreateCategory():
    create_category = CreateCategory()
    if create_category.validate_on_submit():
        category_name = create_category.categoryName.data
        category_description = create_category.categoryDescription.data
        new_category = Category(name=category_name, description=category_description)
        db.session.add(new_category)
        db.session.commit()
        return redirect(url_for('main.adminDashboard'))
    return render_template('adminCreateCategory.html', createNewCategory=create_category)


@main.route('/delete_category/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    category = Category.get(category_id)
    if category:
        try:
            # Delete all products associated with this category
            products = Product.query.filter_by(category_id=category_id).all()
            for product in products:
                db.session.delete(product)

            # Delete the category
            db.session.delete(category)
            db.session.commit()
            flash('Category and associated products deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error deleting category: {str(e)}')
            flash('An error occurred while deleting the category.', 'danger')
    else:
        flash('Category not found.', 'danger')
    return redirect(url_for('main.adminDashboard'))


@main.route('/editCategory/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    form = CreateCategory()
    category = Category.get(category_id)

    if not category:
        flash('Category not found', 'danger')
        return redirect(url_for('main.adminDashboard'))

    if request.method == 'GET':
        form.categoryName.data = category.name
        form.categoryDescription.data = category.description

    if request.method == 'POST' and form.validate_on_submit():
        category.name = form.categoryName.data
        category.description = form.categoryDescription.data
        db.session.commit()
        flash('Category updated successfully!', 'success')
        return redirect(url_for('main.adminDashboard'))

    return render_template('adminEditCategory.html', form=form, category_id=category_id)

#############################
    # Merchant #
#############################

@main.route('/sellerDashboard', methods=['GET'])
@login_required
def sellerDashboard():
    
    # retrieve account details
    user_id = current_user.user_id
    account_details_form = AccountDetailsForm()
    update_business_form = RegisterBusinessForm()
    profile_pic_url = None

    user = User.get(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('main.sellerDashboard'))

    account_details_form.username.data = user.username
    account_details_form.email.data = user.email
    account_details_form.role.data = user.role
    account_details_form.account_status.data = user.account_status
    if user.profile_pic_url:
        profile_pic_url = base64.b64encode(user.profile_pic_url).decode('utf-8')

    # business details
    # Pre-populate the business form with existing merchant data if available
    merchant = Merchant.query.filter_by(user_id=user_id).first()
    if merchant:
        update_business_form.business_name.data = merchant.business_name
        update_business_form.business_address.data = merchant.business_address

        update_business_form.user_id.data = user_id

     # retrieve orders
    orders = Order.query.all()

    # Retrieve products
    products = Product.query.filter_by(merchant_id=merchant.merchant_id).all()    
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
        user = User.get(user_id)
        if user:
            user.username = account_details_form.username.data
            user.email = account_details_form.email.data
            if account_details_form.password.data:
                user.password = generate_password_hash(account_details_form.password.data)
            if account_details_form.profile_picture.data:
                profile_picture = account_details_form.profile_picture.data
                filename = secure_filename(profile_picture.filename)
                user.profile_pic_url = profile_picture.read()
            db.session.commit()
        else:
            flash('User not found', 'danger')
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
                merchant = Merchant.query.filter_by(user_id=user_id).first()
                if merchant:
                    current_app.logger.debug(f"Merchant found: {merchant.business_name}")
                    merchant.business_name = update_business_form.business_name.data
                    merchant.business_address = update_business_form.business_address.data
                    db.session.commit()
                    current_app.logger.debug("Merchant details updated successfully!")
                else:
                    # If the merchant does not exist, create a new one
                    Merchant.create(
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

    # Pre-populate the form with existing merchant data if available
    merchant = Merchant.query.filter_by(user_id=user_id).first()
    if merchant:
        update_business_form.business_name.data = merchant.business_name
        update_business_form.business_address.data = merchant.business_address

    # Set the user_id field to the current user's ID
    update_business_form.user_id.data = user_id

    return render_template('sellerRegBusiness.html', updateBusiness=update_business_form)


@main.route('/update_business', methods=['POST'])
@login_required
def update_business():
    user_id = current_user.user_id
    update_business_form = RegisterBusinessForm()

    if update_business_form.validate_on_submit():
        try:
            merchant = Merchant.query.filter_by(user_id=user_id).first()
            if merchant:
                merchant.business_name = update_business_form.business_name.data
                merchant.business_address = update_business_form.business_address.data

                # Log before commit
                current_app.logger.debug(f"Updating merchant: {merchant}")

                db.session.commit()

                # Log after commit to verify
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

# @main.route('/newProduct', methods=['GET', 'POST'])
# @login_required
# def newProduct():
#     try:
#         form = CreateProductForm()
#         form.productCategoryID.choices = [(c.category_id, c.name) for c in Category.query.all()]

#         if form.validate_on_submit():
#             product_name = form.productName.data
#             product_description = form.productDescription.data 
#             product_category_id = form.productCategoryID.data
#             product_price = form.productPrice.data 
#             product_quantity = form.productQuantity.data 
#             product_created_date = form.productCreatedDate.data 
#             product_last_updated_date = form.productLastUpdated.data 
#             image_data = form.image_url.data.read()
#             create_product = Product(name=product_name, description=product_description, category_id=product_category_id, 
#                                  price=product_price, quantity=product_quantity, created_date=product_created_date, 
#                                  last_updated=product_last_updated_date, image=image_data)
#             db.session.add(create_product)
#             db.session.commit()
#             print("Product added to the database")
#             flash('Product created successfully!', 'success')
#             return redirect(url_for('main.sellerDashboard'))
#         else:
#             print("Form validation failed")
#             for field, errors in form.errors.items():
#                 for error in errors:
#                     print(f"Error in {field}: {error}")

#     except Exception as e:
#         # Log the exception
#         print(f'Error: {e}')
#         flash('An error occurred. Please try again later.', 'danger')
#         return redirect(url_for('main.sellerDashboard'))          

#     return render_template('sellerNewProduct.html', form=form)

@main.route('/newProduct', methods=['GET','POST'])
@login_required
def newProduct():
    print("Initializing CreateProductForm")
    form = CreateProductForm()

    # Load unique categories
    categories = Category.query.all()
    unique_categories = {}
    for c in categories:
        if c.name not in unique_categories:
            unique_categories[c.name] = c.category_id
    form.productCategoryID.choices = [(category_id, name) for name, category_id in unique_categories.items()]

    # Retrieve the merchant_id for the current user
    merchant = Merchant.query.filter_by(user_id=current_user.user_id).first()
    if not merchant:
        flash('No merchant found for the current user.', 'danger')
        return redirect(url_for('main.sellerDashboard'))
        
    # Prepopulate the merchant_id field
    form.merchant_id.data = merchant.merchant_id

    if request.method == 'POST':
        print("Form submitted with POST method")
        print(form.data)  # Debugging statement to print form data
        if form.validate_on_submit():
            print("Form validated successfully")
            product_name = form.productName.data
            product_description = form.productDescription.data
            product_category_id = form.productCategoryID.data
            product_price = form.productPrice.data
            product_quantity = form.productQuantity.data
            product_availability = form.availability.data
            image_data = form.image_url.data.read()  # Read image file as binary data

            # Calculate Singapore time (UTC+8)
            utc_now = datetime.utcnow()
            singapore_time = utc_now + timedelta(hours=8)
            created_date = singapore_time
            last_updated_date = singapore_time

            print(f"Creating product with name: {product_name}, description: {product_description}, "
                f"category_id: {product_category_id}, price: {product_price}, quantity: {product_quantity}, availability: {product_availability}")

            create_product = Product.create(
                name=product_name,
                description=product_description,
                category_id=product_category_id,
                price=product_price,
                quantity=product_quantity,
                availability=product_availability,
                image_url=image_data,
                merchant_id=merchant.merchant_id,  # Use merchant_id from the Merchant table
                created_date = created_date,
                last_updated_date=last_updated_date
            )

            print("Product added to the database")
            flash('Product created successfully!', 'success')
            return redirect(url_for('main.sellerDashboard'))
        else:
            print("Form validation failed")
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Error in {field}: {error}")
    else:
        print("GET request received")

    print("Rendering new product form")
    return render_template('sellerNewProduct.html', form=form)

@main.route('/updateProduct/<int:product_id>', methods=['GET', 'POST'])
@login_required
def updateProduct(product_id):
    form = UpdateProductForm()
    product = Product.query.get(product_id)
    form.productCategoryID.choices = [(c.category_id, c.name) for c in Category.query.all()]
    image_url = None

    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('main.sellerDashboard'))

    # Retrieve the merchant_id for the current user
    merchant = Merchant.query.filter_by(user_id=current_user.user_id).first()
    if not merchant:
        flash('No merchant found for the current user.', 'danger')
        return redirect(url_for('main.sellerDashboard'))
        
    # Prepopulate the merchant_id field
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
        print("Form validated successfully")
        product.name = form.productName.data
        product.description = form.productDescription.data
        product.category_id = form.productCategoryID.data
        product.price = form.productPrice.data
        product.quantity = form.productQuantity.data
        product.availability = form.availability.data

        # Calculate Singapore time (UTC+8)
        utc_now = datetime.utcnow()
        singapore_time = utc_now + timedelta(hours=8)
        product.last_updated_date = singapore_time

        if form.image_url.data:
            image_url = form.image_url.data
            filename = secure_filename(image_url.filename)
            product.image_url = image_url.read()
       
        print(f"Updating product: {product.__dict__}")
        db.session.commit()
        print("Product updated and committed to the database")
        flash('Product updated successfully!', 'success')
        return redirect(url_for('main.sellerDashboard'))

    if request.method == 'POST' and not form.validate_on_submit():
        print("Form validation failed")
        print(form.errors)

    return render_template('sellerUpdateProduct.html', form=form, image_url=image_url, product_id=product_id)

@main.route('/deleteProduct/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!', 'success')
    else:
        flash('Product not found', 'danger')
    return redirect(url_for('main.sellerDashboard'))


@main.route('/session-info')
def session_info():
    user_id = session.get('user_id')
    if user_id:
        return f"Session active for user_id: {user_id}"
    else:
        return "No active session"

