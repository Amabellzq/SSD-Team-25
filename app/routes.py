from flask import Blueprint, g, redirect, url_for, request, render_template
from flask_login import login_user, login_required, current_user
from flask_principal import Identity, identity_changed, Permission, RoleNeed
from .models import User

main_blueprint = Blueprint('main', __name__)

# Define roles
admin_permission = Permission(RoleNeed('Admin'))
merchant_permission = Permission(RoleNeed('Merchant'))
user_permission = Permission(RoleNeed('User'))

@main_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            identity_changed.send(main_blueprint, identity=Identity(user.id))
            return redirect(url_for('main.index'))
    return render_template('login.html')

@main_blueprint.route('/admin')
@login_required
@admin_permission.require(http_exception=403)
def admin():
    result = g.db.session.execute('SELECT * FROM administrator')
    return str(result.fetchall())

@main_blueprint.route('/merchant')
@login_required
@merchant_permission.require(http_exception=403)
def merchant():
    result = g.db.session.execute('SELECT * FROM merchant')
    return str(result.fetchall())

@main_blueprint.route('/user')
@login_required
@user_permission.require(http_exception=403)
def user():
    result = g.db.session.execute('SELECT * FROM user')
    return str(result.fetchall())

@main_blueprint.route('/readonly')
@login_required
def readonly():
    result = g.db.session.execute('SELECT * FROM product')
    return str(result.fetchall())

@main_blueprint.route('/homepage')
def index():
    return render_template('homepage.html')


