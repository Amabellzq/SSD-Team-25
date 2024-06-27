from flask import Blueprint, render_template, jsonify, redirect, url_for, flash, request
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from .templates.includes.forms import LoginForm, RegistrationForm, CheckoutForm, AccountDetailsForm, CreateCategory, EditUserForm
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import base64
from .models import db, User, Category, Merchant, Order, Product, Session, ShoppingCart, CartItem, OrderItem, Payment

main = Blueprint('main', __name__)
login_manager = LoginManager()
login_manager.init_app(main)
login_manager.login_view = 'main.login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/shop')
def shop():
    return render_template('shop.html')

@main.route('/contact')
def contact():
    return render_template('contact.html')

@main.route('/productDetails')
def productDetails():
    return render_template('product-details.html')

@main.route('/myprofile', methods=['GET', 'POST'])
@login_required
def myaccount():
    user_id = current_user.user_id
    account_details_form = AccountDetailsForm()
    profile_pic_url = None

    if request.method == 'GET':
        user = User.get(user_id)
        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('main.adminDashboard'))

        account_details_form.username.data = user.username
        account_details_form.role.data = user.role
        account_details_form.account_status.data = user.account_status
        if user.profile_pic_url:
            profile_pic_url = base64.b64encode(user.profile_pic_url).decode('utf-8')

    if request.method == 'POST' and account_details_form.validate_on_submit():
        user = User.get(user_id)
        if user:
            user.username = account_details_form.username.data
            if account_details_form.password.data:
                user.password = generate_password_hash(account_details_form.password.data)
            if account_details_form.profile_picture.data:
                profile_picture = account_details_form.profile_picture.data
                filename = secure_filename(profile_picture.filename)
                user.profile_pic_url = profile_picture.read()
            db.session.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('main.sellerDashboard'))
        else:
            flash('User not found', 'danger')

    return render_template('account.html', accountDetails=account_details_form, profile_pic_url=profile_pic_url, user=user)

@main.route('/cart')
@login_required
def cart():
    return render_template('cart.html', user=current_user)

@main.route('/checkoutpage', methods=['GET', 'POST'])
@login_required
def checkout():
    form = CheckoutForm()
    if form.validate_on_submit():
        # Process the order here
        return redirect(url_for('main.order_confirmation'))
    return render_template('checkout.html', checkout_form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.get_by_username(username)
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', login_form=form)

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        role = form.role.data
        password = form.password.data
        profile_picture = form.profile_picture.data

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, role=role)

        if profile_picture:
            filename = secure_filename(profile_picture.filename)
            new_user.profile_pic_url = profile_picture.read()

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Thanks for registering!', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    return render_template('register.html', register_form=form)

@main.route('/forgetPW', methods=['GET', 'POST'])
def forgetPass():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash('Please check your email')
        return redirect(url_for('main.login'))
    return render_template('forgetPW.html', resetpass_form=form)

@main.route('/adminDashboard')
@login_required
def adminDashboard():
    users = User.query.all()
    categories = Category.query.all()

    for user in users:
        if user.profile_pic_url:
            user.profile_pic_url = base64.b64encode(user.profile_pic_url).decode('utf-8')

    return render_template('adminDashboard.html', users=users, categories=categories)

@main.route('/editUser/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    form = EditUserForm()
    user = User.get(user_id)

    if not user:
        flash('User not found', 'danger')
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
        flash('User updated successfully!', 'success')
        return redirect(url_for('main.adminDashboard'))

    return render_template('adminManageUser.html', form=form, profile_pic_url=profile_pic_url, user=user)

@main.route('/deleteUser/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    else:
        flash('User not found', 'danger')
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
        flash('Category created successfully!', 'success')
        return redirect(url_for('main.adminDashboard'))
    return render_template('adminCreateCategory.html', createNewCategory=create_category)

@main.route('/deleteCategory/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.get(category_id)
    if category:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully!', 'success')
    else:
        flash('Category not found', 'danger')
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

@main.route('/sellerDashboard', methods=['GET', 'POST'])
@login_required
def sellerDashboard():
    user_id = current_user.user_id
    account_details_form = AccountDetailsForm()
    profile_pic_url = None

    if request.method == 'GET':
        user = User.get(user_id)
        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('main.adminDashboard'))

        account_details_form.username.data = user.username
        account_details_form.role.data = user.role
        account_details_form.account_status.data = user.account_status
        if user.profile_pic_url:
            profile_pic_url = base64.b64encode(user.profile_pic_url).decode('utf-8')

    if request.method == 'POST' and account_details_form.validate_on_submit():
        user = User.get(user_id)
        if user:
            user.username = account_details_form.username.data
            if account_details_form.password.data:
                user.password = generate_password_hash(account_details_form.password.data)
            if account_details_form.profile_picture.data:
                profile_picture = account_details_form.profile_picture.data
                filename = secure_filename(profile_picture.filename)
                user.profile_pic_url = profile_picture.read()
            db.session.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('main.sellerDashboard'))
        else:
            flash('User not found', 'danger')

    return render_template('sellerDashboard.html', accountDetails=account_details_form, profile_pic_url=profile_pic_url, user=user)

@main.route('/orderDetails')
@login_required
def orderDetails():
    return render_template('sellerOrderDetails.html', user=current_user)

@main.route('/newProduct')
@login_required
def newProduct():
    return render_template('sellerNewProduct.html', user=current_user)

@main.route('/updateProduct')
@login_required
def updateProduct():
    return render_template('sellerUpdateProduct.html', user=current_user)

@main.route('/db_check')
def db_check():
    try:
        db_name = db.engine.execute("SELECT DATABASE()").fetchone()[0]
        return jsonify({"status": "success", "database": db_name}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
