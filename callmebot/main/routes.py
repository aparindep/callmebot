from math import floor
from pickletools import optimize
from re import I
from turtle import pos
from flask import get_flashed_messages, redirect, jsonify,render_template, abort, flash
from sqlalchemy import desc
from werkzeug.utils import secure_filename
from pathlib import Path
from PIL import Image

from . import main
from callmebot.models import Reminder
from callmebot import db

from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateField, TimeField
from wtforms.validators import DataRequired, Length, Optional


class ReminderForm(FlaskForm):
    subject = StringField(label='Subject', description='What should be the mail subject?', validators=[Optional(), Length(1,50, 'Subject must have between 5 and 50 characters.')] )
    content = TextAreaField(label='Content', description='What should be the mail content?', validators=[Optional(), Length(1,700, 'Content must have between 1 and 200 characters.')])
    date = DateField(label='Date', description='Which day should the mail be sent?', validators=[DataRequired('A day is required.')])
    time = TimeField(label='Time', description='What time should the mail be sent?', validators=[DataRequired('A time is required.')])
    submit = SubmitField('Add')

@main.route('/')
def index():
    if current_user.is_authenticated:
        reminders = Reminder.query.filter_by(author_id = current_user.id).all()
        print(reminders)
        return render_template('home.html', reminders = reminders)
    else:
        return redirect('/auth/register')

@main.route('/new', methods = ['GET', 'POST'])
@login_required
def upload():
    print(current_user.is_authenticated)
    form = ReminderForm()
    if form.validate_on_submit():
        data = form.data
        r = Reminder(subject=data['subject'], content=data['content'], date=data['date'], time=data['time'], author_id=current_user.id)
        db.session.add(r)
        db.session.commit()
        return redirect('/')
        
    return render_template('new.html', form=form)

# TODO: add delete reminder endpoint
# TODO: add edit reminder endpoint

from uuid import uuid4
def make_unique(string):
    ident = uuid4().__str__()
    return f'{ident}{Path(string).suffix}'