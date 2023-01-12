import pytz
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo
from wtforms import StringField, PasswordField, SubmitField, ValidationError, SelectField
from ..models import User

tzs = [" "] + [tz for tz in pytz.common_timezones if len(tz) != 3] # remove GMT and UTC 

class LoginForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired(),  Length(1,64), Email()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField('Log in')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired(),  Length(1,64), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(1,64),
                                        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, ' 'numbers, dots or underscores')])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    timezone = SelectField('Timezone', choices = tzs, validators = [DataRequired()])
    submit = SubmitField('Submit')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
    
    def validate_user(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username is already registered.')

class UpdatePasswordForm(FlaskForm):
    old_password = PasswordField('Current password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[DataRequired(), EqualTo('new_password2', message='Passwords must match.')])
    new_password2 = PasswordField('Confirm new password', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_new_password(form, field):
        if form.old_password.data == field.data:
            raise ValidationError('Your new password must be different from your current password.')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired(), Email()])
    submit = SubmitField('Submit')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Submit')

