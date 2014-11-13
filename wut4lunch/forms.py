from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, ValidationError, BooleanField, SelectField
from wtforms.validators import InputRequired, Email, Length, EqualTo
from flask.ext.login import current_user
from wut4lunch.models import User


class LoginForm(Form):
    email = StringField('Email Address', validators=[InputRequired('You must enter your email.'), Email()])
    password = PasswordField('Password', validators=[InputRequired('You must enter your password.')])
    submit = SubmitField('Login')


class RegisterForm(Form):
    name = StringField('My name is:', validators=[InputRequired('You must enter your name.')])
    email = StringField('My email is:', validators=[InputRequired('You must enter your email.'), Email()])
    password = PasswordField('My top secret password is:', validators=[InputRequired('You must enter a password.'),
                                                                       Length(8, 20,
                                                                              'Your password must be 8 - 20 characters.'),
                                                                       EqualTo('confirm', 'Passwords must match.')])
    confirm = PasswordField('Confirm your password:', validators=[InputRequired('You must confirm your password.')])
    submit = SubmitField('Sign up')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email has already been registered.')


class ChangePassword(Form):
    old_password = PasswordField('What is your old password?', validators=[InputRequired('You must enter your old password.')])
    new_password = PasswordField('What is your new password?', validators=[InputRequired('You must enter a new password.'),
                                                                       Length(8, 20,
                                                                              'Your password must be 8 - 20 characters.'),
                                                                       EqualTo('confirm', ' New passwords must match.')])
    confirm = PasswordField('Confirm your new password.', validators=[InputRequired('You must confirm your new password.')])
    submit = SubmitField('Change password')

    def validate_password(self, field):
        user = User.query.filter_by(id=current_user.id).first()
        if not user.check_password(field.data):
            raise ValidationError('Old password is not correct.')


class AddLunch(Form):
    lunch = StringField('For lunch, I had:',
                        validators=[InputRequired('You\'ve got to enter what you ate - that\'s the point!')])
    enjoyed = SelectField('I found my lunch:',
                          choices=[('delicious', 'Really delicious'), ('tasty', 'Quite tasty'), ('nice', 'Nice enough'),
                                   ('ok', 'Okay, I guess'), ('nasty', 'Pretty nasty')])
    visible_to = SelectField('My lunch is visible to:',
                             choices=[('all', 'Everyone'), ('followers', 'My followers'), ('me', 'Just me')])
    submit = SubmitField('Share lunch!')
