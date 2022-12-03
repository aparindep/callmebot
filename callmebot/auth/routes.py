from flask import redirect,render_template, flash

from callmebot.auth import bp
from callmebot.models import User
from callmebot import db
from mail import send_email
from flask_login import login_user, current_user, login_required, logout_user


from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo
from wtforms import StringField, PasswordField, SubmitField, ValidationError

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
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
    
    def validate_user(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username is already registered.')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=True)
            return redirect('/')
        else:
            flash('Your email or password is wrong.')
    return render_template('auth/login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        token = user.generate_confirmation_token()
        
        send_email(to=user.email, subject=' New user confirmation', html_body=render_template('email/confirmation.html', name=user.username, token=token))

        return redirect('/')
    return render_template('auth/register.html', form=form)

@bp.route('/confirm/<token>')
@login_required
def confirm(token):
    current_user.confirm(token)
    if current_user.confirm(token) == True:
        flash('You have confirmed your account.')
        return render_template('auth/confirmation.html', token=token)
    else:
        flash('The confirmation token is invalid or has expired.')
        return render_template('expired.html'), 401
        # TODO: add resend_confirmation option when user config view is implemented

@login_required
@bp.route('/logout')
def logout():
    logout_user()
    return redirect('/')
