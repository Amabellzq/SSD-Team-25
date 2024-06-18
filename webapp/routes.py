from flask import Blueprint, render_template, jsonify, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from .templates.includes.forms import LoginForm, RegistrationForm, CheckoutForm, AccountDetailsForm
from .models import User, load_user
from .db import get_db_connection

main = Blueprint('main', __name__)
login_manager = LoginManager()
login_manager.init_app(main)
login_manager.login_view = 'main.login'  # Assuming 'login' is your view function for logging in


# User loader setup
@login_manager.user_loader
def load_user(user_id):
    # Your user loading logic here, for example:
    return User.query.get(int(user_id))  # Adjust this according to your actual database call

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/shop')
def shop():

    return render_template('shop.html')

@main.route('/productDetails')
def productDetails():

    return render_template('product-details.html')


@main.route('/contact')
def contact():

    return render_template('contact.html')

@main.route('/myprofile', methods =['GET', 'POST'])
@login_required
def myaccount():

    account_details_form = AccountDetailsForm()
    if account_details_form.validate_on_submit():

        # Process form data here (e.g., update user details in the database)
        flash('Account details updated successfully.', 'success')
        return redirect(url_for('account_details'))
    return render_template('account.html', accountDetails = account_details_form)


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
        # Example: save the order details, send a confirmation email, etc.
        return redirect(url_for('main.order_confirmation'))
    return render_template('checkout.html', checkout_form = form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get(form.username.data)
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('main.home'))  # Redirect to the standard user page or index        else:
        else:
            flash('Invalid username or password')
    return render_template('login.html', login_form=form)

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Implement your registration logic here
        # For example, create a new user in the database
        flash('Thanks for registering!')
        return redirect(url_for('main.login'))
    return render_template('register.html', register_form=form)

@main.route('/forgetPW', methods=['GET', 'POST'])
def forgetPass():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Implement your registration logic here
        # For example, create a new user in the database
        flash('Please check your email')
        return redirect(url_for('main.login'))
    return render_template('forgetPW.html', resetpass_form=form)


@main.route('/adminDashboard')
@login_required
def adminDashboard():

    account_details_form = AccountDetailsForm()
    if account_details_form.validate_on_submit():

        # Process form data here (e.g., update user details in the database)
        flash('Account details updated successfully.', 'success')
        return redirect(url_for('main.account_details'))
    
    return render_template('adminDashboard.html', accountDetails = account_details_form)

@main.route('/db_check')
def db_check():
    connection = None
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()
            return jsonify({"status": "success", "database": db_name['DATABASE()']}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if connection:
            connection.close()

