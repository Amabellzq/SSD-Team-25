from flask import Blueprint, render_template, jsonify, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from .templates.includes.forms import LoginForm, RegistrationForm, CheckoutForm, AccountDetailsForm, ManageAccountDetailsForm, CreateCategory
from webapp.models import User, load_user
from webapp.db import get_db_connection

main = Blueprint('main', __name__)
login_manager = LoginManager()
login_manager.init_app(main)
login_manager.login_view = 'main.login'  # Assuming 'login' is your view function for logging in


# User loader setup
@login_manager.user_loader
def load_user(user_id):
    # Your user loading logic here, for example:
    return User.query.get(int(user_id))  # Adjust this according to your actual database call

####################################################################################################################
###########################                              BASIC ROUTES                   ############################
####################################################################################################################

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

####################################################################################################################
###########################                           END BASIC ROUTES                  ############################
####################################################################################################################

####################################################################################################################
################                              START REQUIRED  AUTHENTICATION VIEW ROUTES                 ###########
####################################################################################################################

@main.route('/myprofile', methods =['GET', 'POST'])
@login_required
def myaccount():

    account_details_form = AccountDetailsForm()
    if account_details_form.validate_on_submit():

        # Process form data here (e.g., update user details in the database)
        flash('Account details updated successfully.', 'success')
        return redirect(url_for('account_details'))
    return render_template('account.html', accountDetails = account_details_form)

#######################################################################
########                       BUYER ROUTES                   #########
#######################################################################

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

####################################################################################################################
################                              END REQUIRED  AUTHENTICATION VIEW ROUTES                   ###########
####################################################################################################################


####################################################################################################################
################################                AUTHENTICATION ROUTES                    ###########################
####################################################################################################################

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

####################################################################################################################
###########################               END AUTHENTICATION ROUTES                    #############################
####################################################################################################################

####################################################################################################################
################################                ADMIN ROUTES                    ####################################
####################################################################################################################

@main.route('/adminDashboard')
@login_required
def adminDashboard():
    
    return render_template('adminDashboard.html')

@main.route('/ManageUser')
@login_required
def adminManageUser():

    manage_Useraccount_details_form = ManageAccountDetailsForm()
    if manage_Useraccount_details_form.validate_on_submit():

        # Process form data here (e.g., update user details in the database)
        flash('Account details updated successfully.', 'success')
        return redirect(url_for('main.account_details'))
    
    return render_template('adminManageUser.html', manageAccountInfo = manage_Useraccount_details_form)

####################################################################################################################
################################               END ADMIN ROUTES                    #################################
####################################################################################################################

####################################################################################################################
################################                MERCHANT ROUTES                    #################################
####################################################################################################################

@main.route('/sellerDashboard')
@login_required
def sellerDashboard():

    account_details_form = AccountDetailsForm()
    if account_details_form.validate_on_submit():

        # Process form data here (e.g., update user details in the database)
        flash('Account details updated successfully.', 'success')
        return redirect(url_for('main.sellerDashboard'))
    
    # Query the database for category data
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Category")
            categories = cursor.fetchall()
    except Exception as e:
        flash(f"An error occurred while fetching categories: {str(e)}", 'danger')
        categories = []

    
    return render_template('sellerDashboard.html', accountDetails = account_details_form, categories = categories)

@main.route('/orderDetails')
@login_required
def orderDetails():

    return render_template('sellerOrderDetails.html', user=current_user)

@main.route('/createCategory', methods=['GET', 'POST'])
@login_required
def merchantCreateCategory():

    create_category = CreateCategory()
    if create_category.validate_on_submit():
        category_name = create_category.categoryName.data
        category_description = create_category.categoryDescription.data
        # Insert category into database
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                sql = "INSERT INTO Category (name, description) VALUES (%s, %s)"
                cursor.execute(sql, (category_name, category_description))
                conn.commit()
                print("Database insert successful")  # Debug
            # Process form data here (e.g., update user details in the database)
            flash('Account details updated successfully.', 'success')
            return redirect(url_for('main.sellerDashboard'))
        except Exception as e:
            print(f"Database error: {str(e)}")  # Debug
            flash(f'An error occurred: {str(e)}', 'danger')
    else:
        if request.method == 'POST':
            print("Form validation failed")  # Debug
            flash('Form validation failed. Please check your input.', 'danger')
    return render_template('sellerCreateCategory.html', createNewCategory = create_category)


####################################################################################################################
################################               END MERCHANT ROUTES                    ##############################
####################################################################################################################

#Example on how the database connection is called
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

