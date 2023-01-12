from sqlalchemy import update
from flask import redirect,render_template, flash
from flask_login import login_user, current_user, login_required, logout_user

from . import bp
from .forms import RegistrationForm, LoginForm
from .. import db, login_manager
from ..models import User
from ..email import send_email

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
        
        send_email(to=user.email, subject=' New user confirmation', content=render_template('email/confirmation.html', name=user.username, token=token))

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

@bp.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(to=current_user.email, subject=' New user confirmation', content=render_template('email/confirmation.html', name=current_user.username, token=token))
    flash('Confirmation email has been sent.')
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

        flash('Sucessfuly edited your profile.')
        return redirect('/')
    
    return render_template('auth/edit.html', form = form)
        

@login_required
@bp.route('/logout')
def logout():
    logout_user()
    return redirect('/')
