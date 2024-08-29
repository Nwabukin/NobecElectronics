from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FileField
from wtforms.widgets import NumberInput  # For HTML5 number input type
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, Optional
from phonenumbers import parse, is_valid_number  # For phone number validation
from app.models import User  # Import your User model


class RegistrationForm(FlaskForm):
    """Form for user registration."""

    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    street_address = StringField('Street Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    postal_code = StringField('Postal Code', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)], widget=NumberInput())

    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        """Custom validator to check if username is unique."""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        """Custom validator to check if email is unique."""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

    def validate_phone_number(self, phone_number):
        """Custom validator to validate phone number using phonenumbers library."""
        try:
            p = parse(phone_number.data, "NG")  # 'NG' is the country code for Nigeria
            if not is_valid_number(p):
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError('Invalid phone number.')


class LoginForm(FlaskForm):
    """Form for user login."""

    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    street_address = StringField('Street Address', validators=[Optional()])
    city = StringField('City', validators=[Optional()])
    state = StringField('State', validators=[Optional()])
    country = StringField('Country', validators=[Optional()])
    postal_code = StringField('Postal Code', validators=[Optional()])
    phone_number = StringField('Phone Number', validators=[Optional(), Length(min=10, max=20)])
    about_me = TextAreaField('About Me', validators=[Length(max=140)])
    profile_picture = FileField('Profile Picture', validators=[Optional()])

    submit = SubmitField('Save Changes')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=self.email.data).first()
            if user is not None:
                raise ValidationError('That email is taken. Please choose a different one.')
    
    def validate_phone_number(self, phone_number):
        """Custom validator to validate phone number using phonenumbers library."""
        if phone_number.data:
            try:
                p = parse(phone_number.data, "NG")  # 'NG' is the country code for Nigeria
                if not is_valid_number(p):
                    raise ValueError()
            except (ValueError, TypeError):
                raise ValidationError('Invalid phone number.')