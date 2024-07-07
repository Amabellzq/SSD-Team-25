from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, BooleanField, SelectField, FileField, DecimalField, ValidationError, IntegerField, DateTimeField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, NumberRange, Optional
from flask_wtf.file import FileRequired, FileAllowed
import re
import requests, hashlib

#############################
    #Authentication#
#############################

class NISTPasswordPolicy:
    def __init__(self, min_length=8, max_length=64, message=None):
        self.min_length = min_length
        self.max_length = max_length
        if not message:
            self.message = f"Password must be between {min_length} and {max_length} characters."
        else:
            self.message = message
    
    def __call__(self, form, field):
        password = field.data
        errors = []
        
        if not (self.min_length <= len(password) <= self.max_length):
            errors.append(self.message)

        # Prohibit sequences of the same character
        if self.has_successive_chars(password):
            errors.append('Password cannot contain successive identical characters.')
        
        if self.has_consecutive_chars(password):
            errors.append('Password cannot contain consecutive characters.')
        
        if self.is_breached_password(password):
            errors.append('This password has been exposed in a data breach, Please choose a different password.')

        if errors:
            raise ValidationError(" ".join(errors))

    def has_successive_chars(self, password):
        for i in range(len(password) - 1):
            if password[i] == password[i + 1]:
                return True
        return False
    
    def has_consecutive_chars(self, password):
        for i in range(len(password) - 3):
            if (ord(password[i]) == ord(password[i + 1]) - 1 == ord(password[i + 2]) - 2 == ord(password[i + 3]) - 3 or
                ord(password[i]) == ord(password[i + 1]) + 1 == ord(password[i + 2]) + 2 == ord(password[i + 3]) + 3):
                return True
        return False
    
    def is_breached_password(self, password):
        sha1_password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix = sha1_password[:5]
        suffix = sha1_password[5:]
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        response = requests.get(url)
        if response.status_code != 200:
            raise ValidationError('Error checking password breach status.')
        
        hashes = (line.split(':') for line in response.text.splitlines())
        for h, count in hashes:
            if suffix == h:
                return True
        return False

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Regexp(r'^\S+@\S+\.\S+$', message="Invalid Email")])    
    role = SelectField('I am a', choices=[ ('Customer', 'Customer'), ('Merchant', 'Merchant'), ('Admin', 'Admin')], validators=[DataRequired()])
    profile_picture = FileField('Set Profile Picture', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    password = PasswordField('Password', validators=[DataRequired(), NISTPasswordPolicy()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message="Password must match")])
    submit = SubmitField('Register')

class ResetPasswordForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset Password')

class TOTPForm(FlaskForm):
    totp = StringField('TOTP Code', validators=[DataRequired()])
    submit = SubmitField('Verify')

class OTPForm(FlaskForm):
    otp = StringField('OTP Code', validators=[DataRequired()])
    submit = SubmitField('Verify')

#############################
    # Purchase #
#############################

class CheckoutForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    address2 = StringField('Address 2')
    postcode = StringField('Postcode/Zip', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])  # Removed Email() validator
    payment_method = SelectField('Payment Method', choices=[('Credit Card', 'Credit Card'), ('Debit Card', 'Debit Card')], validators=[DataRequired()])
    submit = SubmitField('Place order')

class AddToCart(FlaskForm):
    product_id = HiddenField('Product ID')
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Add to cart')

class UpdateCartForm(FlaskForm):
    cart_item_id = HiddenField('Cart Item ID', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Update Cart')
    
#############################
    # Account #
#############################

class AccountDetailsForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    profile_picture = FileField('Profile Picture', validators=[ FileAllowed(['jpg', 'png'], 'Images only!')])
    email = StringField('Email', validators=[DataRequired(), Regexp(r'^\S+@\S+\.\S+$', message="Invalid Email")])    
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
    # Admin #
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

class CreateProductForm(FlaskForm):
    productName = StringField('Product Name', validators=[DataRequired()])
    productDescription = StringField('Product Description', validators=[DataRequired()])
    productCategoryID = SelectField('Category', coerce=int, validators=[DataRequired()])
    productPrice = DecimalField('Price', validators=[DataRequired()])
    productQuantity = IntegerField('Quantity', validators=[DataRequired()])
    availability = SelectField('Availability', choices=[ ('In Stock', 'In Stock')], validators=[DataRequired()])
    image_url = FileField('Product Image', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    merchant_id = IntegerField('Merchant ID', validators=[DataRequired(), NumberRange(min=1)])
    productCreatedDate = DateTimeField('Created Date', validators=[Optional()], render_kw={'readonly': True})
    productLastUpdated = DateTimeField('Last Updated Date', validators=[Optional()], render_kw={'readonly': True})
    submit = SubmitField('Create')

class UpdateProductForm(FlaskForm):
    productName = StringField('Product Name', validators=[DataRequired()])
    productDescription = StringField('Product Description', validators=[DataRequired()])
    productCategoryID = SelectField('Category', coerce=int, validators=[DataRequired()])
    productPrice = DecimalField('Price', validators=[DataRequired()])
    productQuantity = IntegerField('Quantity', validators=[DataRequired()])
    availability = SelectField('Availability', choices=[ ('In Stock', 'In Stock'), ('Out of Stock', 'Out of Stock')], validators=[DataRequired()])
    image_url = FileField('Product Image', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    merchant_id = IntegerField('Merchant ID', validators=[DataRequired(), NumberRange(min=1)], render_kw={'readonly': True})
    productCreatedDate = DateTimeField('Created Date', validators=[Optional()], render_kw={'readonly': True})
    productLastUpdated = DateTimeField('Last Updated Date', validators=[Optional()], render_kw={'readonly': True})
    submit = SubmitField('Update Product')