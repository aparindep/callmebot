from sqlalchemy import update
from flask import redirect,render_template, flash
from flask_login import login_user, current_user, login_required, logout_user

from . import bp
from forms import RegistrationForm, LoginForm, UpdatePasswordForm, ResetPasswordRequestForm, ResetPasswordForm
from .. import db, login_manager
from ..models import User
from ..email import send_email, send_password_reset_email

@login_manager.unauthorized_handler
def unauthorized_rollback():
    return redirect('/auth/register')

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
        user = User(email=form.email.data, username=form.username.data, timezone = form.timezone.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        token = user.generate_confirmation_token()
        
        send_email.delay(to=user.email, subject=' New user confirmation', content=render_template('email/confirmation.html', name=user.username, token=token))

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
        return render_template('auth/expired.html'), 401

@bp.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email.delay(to=current_user.email, subject=' New user confirmation', content=render_template('email/confirmation.html', name=current_user.username, token=token))
    flash('I have sent you a confirmation email.')
    return redirect('/')

@bp.route('/edit', methods = ['GET', 'POST'])
@login_required
def edit():
    form = RegistrationForm(
        username = current_user.username,
        timezone = current_user.timezone
    )

    del form.email
    del form.password
    del form.password2

    if form.validate_on_submit():
        data = form.data
        
        stmt = (
            update(User).
            where(User.id == current_user.id).
            values(
                username = data['username'],
                timezone = data['timezone']
                )
            )
        db.session.execute(stmt)
        db.session.commit()

        flash('Sucessfully edited your profile.')
        return redirect('/')
    
    return render_template('auth/edit.html', form = form)
        
@login_required
@bp.route('/edit/update_password', methods=['GET', 'POST'])
def update_password():
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.old_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
        else:
            flash('Your current password is wrong.')
        flash('Succesfully updated your password.')
        return redirect('/')
    return render_template('auth/update_password.html', form=form)

@bp.route('/request_password_reset', methods=['GET', 'POST'])
def request_password_reset():
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user:
           send_password_reset_email(user)
           flash('I have sent you an email to reset your password.')
           return redirect('/auth/login')
    return render_template('auth/req_password_reset.html', form=form)

@bp.route('/reset_password/<token>', methods = ['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect('/')
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect('/')
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Successfully reset your password.')
        return redirect('/auth/login')
    return render_template('auth/reset_password.html', form=form)

@login_required
@bp.route('/logout')
def logout():
    logout_user()
    return redirect('/')
