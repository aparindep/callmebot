from flask import redirect,render_template
from sqlalchemy import update
from pathlib import Path
import datetime

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
    time = TimeField(label='Time', description='What time should the mail be sent?', validators=[DataRequired('A time is required.')], default=datetime.time(0,0))
    submit = SubmitField('Add')

@main.route('/')
def index():
    if current_user.is_authenticated:
        reminders = Reminder.query.filter_by(author_id = current_user.id).all()
        return render_template('home.html', reminders = reminders)
    else:
        return redirect('/auth/register')

@main.route('/new', methods = ['GET', 'POST'])
@login_required
def upload():
    form = ReminderForm()
    if form.validate_on_submit():
        data = form.data
        r = Reminder(
            subject=data['subject'],
            content=data['content'],
            date=data['date'],
            time=data['time'],
            author_id=current_user.id
            )
        db.session.add(r)
        db.session.commit()
        return redirect('/')
        
    return render_template('new.html', form=form)

@main.route('/edit/<reminder_id>', methods=['GET', 'POST'])
def edit(reminder_id):
    r = Reminder.query.filter_by(id = reminder_id).first()
    form = ReminderForm(
            subject = r.subject,
            content = r.content,
            date = r.date,
            time = r.time
            )
    form.submit = SubmitField('Edit')
    if form.validate_on_submit():
        data = form.data
        stmt = (
            update(Reminder).
            where(Reminder.id == r.id).
            values(
                subject=data['subject'],
                content=data['content'],
                date=data['date'],
                time=data['time'],
                author_id=current_user.id)
                )
        db.session.execute(stmt)
        db.session.commit()

        return redirect('/')
    return render_template('edit_reminder.html', form=form)

@main.route('/delete/<reminder_id>', methods=['POST'])
def delete(reminder_id):
    r = Reminder.query.filter_by(id = reminder_id).first()
    db.session.delete(r)
    db.session.commit()
    return redirect('/')

from uuid import uuid4
def make_unique(string):
    ident = uuid4().__str__()
    return f'{ident}{Path(string).suffix}'