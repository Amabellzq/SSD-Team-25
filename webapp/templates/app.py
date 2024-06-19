from flask import jsonify, Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from templates.includes.forms import LoginForm, RegistrationForm, CheckoutForm, AccountDetailsForm
from models import User, load_user

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
bootstrap = Bootstrap(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

login_manager.user_loader(load_user)

@app.route('/')
def index():

    return render_template('index.html')

@app.route('/shop')
def shop():

    return render_template('shop.html')

@app.route('/productDetails')
def productDetails():

    return render_template('product-details.html')


@app.route('/contact')
def contact():

    return render_template('contact.html')

@app.route('/myprofile', methods =['GET', 'POST'])
@login_required
def myaccount():

    account_details_form = AccountDetailsForm()
    if account_details_form.validate_on_submit():

        # Process form data here (e.g., update user details in the database)
        flash('Account details updated successfully.', 'success')
        return redirect(url_for('account_details'))
    return render_template('account.html', accountDetails = account_details_form)


@app.route('/cart')
@login_required
def cart():

    return render_template('cart.html', user=current_user)

@app.route('/checkoutpage', methods=['GET', 'POST'])
@login_required
def checkout():
    form = CheckoutForm()
    if form.validate_on_submit():
        # Process the order here
        # Example: save the order details, send a confirmation email, etc.
        return redirect(url_for('order_confirmation'))
    return render_template('checkout.html', checkout_form = form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get(form.username.data)
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('main.index'))  # Redirect to the standard user page or index        else:
        else:
            flash('Invalid username or password')
    return render_template('login.html', login_form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Implement your registration logic here
        # For example, create a new user in the database
        flash('Thanks for registering!')
        return redirect(url_for('main.login'))
    return render_template('register.html', register_form=form)

@app.route('/forgetPW', methods=['GET', 'POST'])
def forgetPass():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Implement your registration logic here
        # For example, create a new user in the database
        flash('Please check your email')
        return redirect(url_for('main.login'))
    return render_template('forgetPW.html', resetpass_form=form)


@app.route('/adminDashboard')
@login_required
def adminDashboard():

    account_details_form = AccountDetailsForm()
    if account_details_form.validate_on_submit():

        # Process form data here (e.g., update user details in the database)
        flash('Account details updated successfully.', 'success')
        return redirect(url_for('account_details'))
    
    return render_template('adminDashboard.html', accountDetails = account_details_form)


if __name__ == '__main__':
    
    app.run(debug=True)