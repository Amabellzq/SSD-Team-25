from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, BooleanField, SelectField, FileField, DecimalField, ValidationError, IntegerField, DateTimeField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, NumberRange
from flask_wtf.file import FileRequired, FileAllowed
import re

#############################
    #Authentication#
#############################

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Regexp(r'^\S+@\S+\.\S+$', message="Invalid Email")])    
    role = SelectField('I am a', choices=[ ('Customer', 'Customer'), ('Merchant', 'Merchant'), ('Admin', 'Admin')], validators=[DataRequired()])
    profile_picture = FileField('Set Profile Picture', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=40)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message="Password must match")])
    submit = SubmitField('Register')

class ResetPasswordForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset Password')

#############################
    # Purchase #
#############################

class CheckoutForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    address2 = StringField('Apartment, suite, etc. (optional)')
    postcode = StringField('Postcode/Zip', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=10, message="Please enter a valid phone number.")])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Place Order')

#############################
    # Account #
#############################

class AccountDetailsForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    profile_picture = FileField('Profile Picture', validators=[ FileAllowed(['jpg', 'png'], 'Images only!')])
    role = SelectField('Role', choices=[ ('Customer', 'Customer'), ('Merchant', 'Merchant'), ('Admin', 'Admin')], validators=[DataRequired()])
    account_status = SelectField('Account Status', choices=[('Active', 'Active'), ('Inactive', 'Inactive'), ('Suspended', 'Suspended')], validators=[DataRequired()])
    password = PasswordField('New Password', validators=[Length(min=0, max=40)])
    submit = SubmitField('Update Details')

class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    role = SelectField('Role', choices=[ ('Customer', 'Customer'), ('Merchant', 'Merchant'), ('Admin', 'Admin')], validators=[DataRequired()])
    account_status = SelectField('account Status', choices=[ ('Active', 'Active'), ('InActive', 'InActive'), ('Suspended', 'Suspended')], validators=[DataRequired()])
    submit = SubmitField('Save')

#############################
    # ADMIN #
#############################

class CreateCategory(FlaskForm):
    categoryName = StringField('Category Name', validators=[DataRequired()])
    categoryDescription = StringField('Category Description', validators=[DataRequired()])
    saveCategory = SubmitField('Save Category')

#############################
    # Merchant #
#############################

class RegisterBusinessForm(FlaskForm):
    user_id = IntegerField('User ID', validators=[DataRequired(), NumberRange(min=1)])
    business_name = StringField('Business Name', validators=[DataRequired(), Length(min=4, max=100)])
    business_address = StringField('Business Address', validators=[DataRequired(), Length(min=10, max=255)])
    submit = SubmitField('Submit Details')

class UpdateProductForm(FlaskForm):
    productID = StringField('Product ID', validators=[DataRequired()], render_kw={'readonly': True})
    productName = StringField('Product Name', validators=[DataRequired()])
    productDescription = StringField('Product Description', validators=[DataRequired()])
    productCategoryID = SelectField('Category', validators=[DataRequired()], choices=[])
    productPrice = DecimalField('Price', validators=[DataRequired()])
    productQuantity = IntegerField('Quantity', validators=[DataRequired()])
    productCreatedDate = DateTimeField('Created Date', validators=[Optional()], render_kw={'readonly': True})
    productLastUpdated = DateTimeField('Last Updated Date', validators=[Optional()], render_kw={'readonly': True})
    submit = SubmitField('Update Product')