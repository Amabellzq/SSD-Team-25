from flask import Blueprint, render_template, jsonify, redirect, url_for, flash, request
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from .templates.includes.forms import LoginForm, RegistrationForm, CheckoutForm, AccountDetailsForm, CreateCategory, EditUserForm
from webapp.models import User, load_user
from webapp.db import get_db_connection
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import base64


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

    print("Request method:", request.method)
    user_id = current_user.id  # Assuming you have `current_user` from Flask-Login

    ###############  ACCOUNT DETAILS ###############
    account_details_form = AccountDetailsForm()
    profile_pic_url = None

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            if request.method == 'GET':
                print("Fetching user from database...")
                cursor.execute("SELECT * FROM User WHERE user_id = %s", (user_id,))
                user = cursor.fetchone()
                if not user:
                    flash('User not found', 'danger')
                    return redirect(url_for('main.adminDashboard'))

                # Prepopulate the form with existing user data
                account_details_form.username.data = user['username']
                account_details_form.role.data = user['role']
                account_details_form.account_status.data = user['account_status']
            
                if user['profile_pic_url']:
                    profile_pic_url = base64.b64encode(user['profile_pic_url']).decode('utf-8')

        if request.method == 'POST':
            print("POST request received.")
            try:
                if account_details_form.validate_on_submit():
                    print("Form validated successfully.")
                    username = account_details_form.username.data
                    password = account_details_form.password.data
                    profile_picture = account_details_form.profile_picture.data
                
                    # Hash the password if it is provided
                    hashed_password = generate_password_hash(password) if password else None

                    # Prepare SQL update statement
                    sql_update_fields = ["username = %s"]
                    sql_update_values = [username]

                    if hashed_password:
                        sql_update_fields.append("password = %s")
                        sql_update_values.append(hashed_password)

                    if profile_picture:
                        filename = secure_filename(profile_picture.filename)
                        picture_data = profile_picture.read()
                        sql_update_fields.append("profile_pic_url = %s")
                        sql_update_values.append(picture_data)

                    sql_update_values.append(user_id)

                    print("SQL update fields:", sql_update_fields)
                    print("SQL update values:", sql_update_values)

                    try:
                        with conn.cursor() as cursor:
                            sql = f"""
                            UPDATE User SET {", ".join(sql_update_fields)} WHERE user_id = %s
                            """
                            print("Executing SQL:", sql)
                            cursor.execute(sql, tuple(sql_update_values))
                            conn.commit()
                            print("Database update successful.")
                        flash('User updated successfully!', 'success')
                        return redirect(url_for('main.sellerDashboard'))
                    
                    except Exception as e:
                        print(f"Database error: {str(e)}")  # Debug
                        flash(f'An error occurred: {str(e)}', 'danger')
                else:
                    print("Form validation failed")  # Debug
                    for field, errors in account_details_form.errors.items():
                        for error in errors:
                            print(f"Error in {field}: {error}")
                    flash('Form validation failed. Please check your input.', 'danger')

            except Exception as e:
                print(f"Error during form submission: {str(e)}")  # Debug
                flash(f'An unexpected error occurred: {str(e)}', 'danger')

    except Exception as e:
        print(f"Error: {str(e)}")  # Debug
        
    finally:
        conn.close()
    ###############   END ACCOUNT DETAILS ###############

    return render_template('account.html', accountDetails = account_details_form, profile_pic_url = profile_pic_url, user=user)

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
        username = form.username.data
        password = form.password.data

        conn = None

        try:
            print("Attempting to get a database connection")
            conn = get_db_connection()
            print("Database connection established")
            with conn.cursor() as cursor:
                sql = "SELECT * FROM User WHERE username = %s"
                cursor.execute(sql, (username,))
                user = cursor.fetchone()
            
            if user:
                print(f"User found: {user['username']}")
            else:
                print("User not found")

            if user and check_password_hash(user['password'], password):
                # Assuming `User` class and `login_user` are set up for Flask-Login
                login_user(User(user))  # You need to implement User class for Flask-Login
                return redirect(url_for('main.home'))  # Redirect to the standard user page or index
            else:
                flash('Invalid username or password', 'danger')

        except Exception as e:
            if conn:
                print("Closing database connection")
                conn.close()
            else:
                print("Connection was not established")

        finally:
            conn.close()
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

        # Save the profile picture
        filename = secure_filename(profile_picture.filename)
        picture_data = profile_picture.read()

        # Hash the password for security
        hashed_password = generate_password_hash(password)

        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                sql = """
                INSERT INTO User (username, password, profile_pic_url, role, account_status)
                VALUES (%s, %s, %s, %s, 'Active')
                """
                cursor.execute(sql, (username, hashed_password, picture_data, role))
                conn.commit()
            flash('Thanks for registering!', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            print(f"Database error: {str(e)}")  # Debug
            flash(f'An error occurred: {str(e)}', 'danger')
        finally:
            conn.close()
    else:
        if request.method == 'POST':
            print("Form validation failed")  # Debug
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Error in {field}: {error}")
            flash('Form validation failed. Please check your input.', 'danger')
            
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

    #VIEW Users - DISPLAY USERS IN A TABLE
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM User")
            users = cursor.fetchall()

            # Encode the profile pictures to Base64
            for user in users:
                if user['profile_pic_url']:
                    user['profile_pic_url'] = base64.b64encode(user['profile_pic_url']).decode('utf-8')

    except Exception as e:
        flash(f"An error occurred while fetching categories: {str(e)}", 'danger')
        users = []

    #CREATE CATEGORIES - DISPLAY CATEGORY DATA TO A TABLE
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Category")
            categories = cursor.fetchall()
    except Exception as e:
        flash(f"An error occurred while fetching categories: {str(e)}", 'danger')
        categories = []

    return render_template('adminDashboard.html', users = users, categories = categories)

@main.route('/editUser/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    form = EditUserForm()
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM User WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                flash('User not found', 'danger')
                return redirect(url_for('main.adminDashboard'))

        if form.validate_on_submit():
            account_status = form.account_status.data
            print(f"Updating user: {user_id} with role: account_status: {account_status}")  # Debug
            try:
                with conn.cursor() as cursor:
                    sql = """
                    UPDATE User SET account_status = %s WHERE user_id = %s
                    """
                    cursor.execute(sql, (account_status, user_id))
                    conn.commit()
                    print("Database update successful")  # Debug
                flash('User updated successfully!', 'success')
                return redirect(url_for('main.adminDashboard'))
            except Exception as e:
                print(f"Database error: {str(e)}")  # Debug
                flash(f'An error occurred: {str(e)}', 'danger')
        else:
            if request.method == 'POST':
                print("Form validation failed")  # Debug
                for field, errors in form.errors.items():
                    for error in errors:
                        print(f"Error in {field}: {error}")
                flash('Form validation failed. Please check your input.', 'danger')
    finally:
        conn.close()

    # Prepopulate the form with existing user data
    form.username.data = user['username']
    form.role.data = user['role']
    form.account_status.data = user['account_status']

    # Pass the profile picture for display
    profile_pic_url = None
    if user['profile_pic_url']:
        profile_pic_url = base64.b64encode(user['profile_pic_url']).decode('utf-8')

    return render_template('adminManageUser.html', form=form, profile_pic_url=profile_pic_url, user=user)

@main.route('/deleteUser/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Check if user exists
            cursor.execute("SELECT * FROM User WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                flash('User not found', 'danger')
                return redirect(url_for('main.adminDashboard'))

            # Delete the user
            cursor.execute("DELETE FROM User WHERE user_id = %s", (user_id,))
            conn.commit()
            flash('User deleted successfully!', 'success')
    except Exception as e:
        print(f"Database error: {str(e)}")  # Debug
        flash(f'An error occurred: {str(e)}', 'danger')
    finally:
        if conn:
            conn.close()
    return redirect(url_for('main.adminDashboard'))


@main.route('/createCategory', methods=['GET', 'POST'])
@login_required
def adminCreateCategory():

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
            return redirect(url_for('main.adminDashboard'))
        except Exception as e:
            print(f"Database error: {str(e)}")  # Debug
            flash(f'An error occurred: {str(e)}', 'danger')
    else:
        if request.method == 'POST':
            print("Form validation failed")  # Debug
            flash('Form validation failed. Please check your input.', 'danger')
    return render_template('adminCreateCategory.html', createNewCategory = create_category)

@main.route('/deleteCategory/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "DELETE FROM Category WHERE category_id = %s"
            cursor.execute(sql, (category_id,))
            conn.commit()
        flash('Category deleted successfully.', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('main.adminDashboard'))

@main.route('/editCategory/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):

    form = CreateCategory()
    if request.method == 'POST' and form.validate_on_submit():
        category_name = form.categoryName.data
        category_description = form.categoryDescription.data
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                sql = "UPDATE Category SET name = %s, description = %s WHERE category_id = %s"
                cursor.execute(sql, (category_name, category_description, category_id))
                conn.commit()
            flash('Category updated successfully.', 'success')
            return redirect(url_for('main.adminDashboard'))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
    else:
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM Category WHERE category_id = %s", (category_id,))
                category = cursor.fetchone()
                if category:
                    form.categoryName.data = category['name']
                    form.categoryDescription.data = category['description']
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
        finally:
            conn.close()

    return render_template('adminEditCategory.html', form=form, category_id=category_id)

####################################################################################################################
################################               END ADMIN ROUTES                    #################################
####################################################################################################################

####################################################################################################################
################################                MERCHANT ROUTES                    #################################
####################################################################################################################

@main.route('/sellerDashboard', methods=['GET', 'POST'])
@login_required
def sellerDashboard():
    print("Request method:", request.method)
    user_id = current_user.id  # Assuming you have `current_user` from Flask-Login

    ###############  ACCOUNT DETAILS ###############
    account_details_form = AccountDetailsForm()
    profile_pic_url = None

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            if request.method == 'GET':
                print("Fetching user from database...")
                cursor.execute("SELECT * FROM User WHERE user_id = %s", (user_id,))
                user = cursor.fetchone()
                if not user:
                    flash('User not found', 'danger')
                    return redirect(url_for('main.adminDashboard'))

                # Prepopulate the form with existing user data
                account_details_form.username.data = user['username']
                account_details_form.role.data = user['role']
                account_details_form.account_status.data = user['account_status']
            
                if user['profile_pic_url']:
                    profile_pic_url = base64.b64encode(user['profile_pic_url']).decode('utf-8')

        if request.method == 'POST':
            print("POST request received.")
            try:
                if account_details_form.validate_on_submit():
                    print("Form validated successfully.")
                    username = account_details_form.username.data
                    password = account_details_form.password.data
                    profile_picture = account_details_form.profile_picture.data
                
                    # Hash the password if it is provided
                    hashed_password = generate_password_hash(password) if password else None

                    # Prepare SQL update statement
                    sql_update_fields = ["username = %s"]
                    sql_update_values = [username]

                    if hashed_password:
                        sql_update_fields.append("password = %s")
                        sql_update_values.append(hashed_password)

                    if profile_picture:
                        filename = secure_filename(profile_picture.filename)
                        picture_data = profile_picture.read()
                        sql_update_fields.append("profile_pic_url = %s")
                        sql_update_values.append(picture_data)

                    sql_update_values.append(user_id)

                    print("SQL update fields:", sql_update_fields)
                    print("SQL update values:", sql_update_values)

                    try:
                        with conn.cursor() as cursor:
                            sql = f"""
                            UPDATE User SET {", ".join(sql_update_fields)} WHERE user_id = %s
                            """
                            print("Executing SQL:", sql)
                            cursor.execute(sql, tuple(sql_update_values))
                            conn.commit()
                            print("Database update successful.")
                        flash('User updated successfully!', 'success')
                        return redirect(url_for('main.sellerDashboard'))
                    
                    except Exception as e:
                        print(f"Database error: {str(e)}")  # Debug
                        flash(f'An error occurred: {str(e)}', 'danger')
                else:
                    print("Form validation failed")  # Debug
                    for field, errors in account_details_form.errors.items():
                        for error in errors:
                            print(f"Error in {field}: {error}")
                    flash('Form validation failed. Please check your input.', 'danger')

            except Exception as e:
                print(f"Error during form submission: {str(e)}")  # Debug
                flash(f'An unexpected error occurred: {str(e)}', 'danger')

    except Exception as e:
        print(f"Error: {str(e)}")  # Debug
        
    finally:
        conn.close()


    ###############   END ACCOUNT DETAILS ###############


    return render_template('sellerDashboard.html',  accountDetails=account_details_form, profile_pic_url=profile_pic_url, user=user)



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

