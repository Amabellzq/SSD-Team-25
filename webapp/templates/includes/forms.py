from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, BooleanField, SelectField, FileField, DecimalField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, NumberRange
from flask_wtf.file import FileRequired, FileAllowed

#############################
    #Authentication#
#############################

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    role = SelectField('I am a', choices=[ ('Customer', 'Customer'), ('Merchant', 'Merchant'), ('Admin', 'Admin')], validators=[DataRequired()])
    profile_picture = FileField('Profile Picture', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
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
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=40)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message="Password must match")])
    submit = SubmitField('Update Details')

class ManageAccountDetailsForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    contact = StringField('Contact Number', validators=[
            DataRequired(),
            Regexp(r'^\d{8}$', message="Contact number must be exactly 8 digits.")
        ]) 
    role = SelectField('I am a', choices=[
            ('user', 'User'),
            ('seller', 'Seller')
        ], validators=[DataRequired()])
    submit = SubmitField('Update Details')


#############################
    # Merchant #
#############################


class CreateCategory(FlaskForm):
    categoryName = StringField('Category Name', validators=[DataRequired()])
    categoryDescription = StringField('Category Description', validators=[DataRequired()])
    saveCategory = SubmitField('Save Category')


