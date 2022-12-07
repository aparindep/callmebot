import datetime

from flask import redirect,render_template
from sqlalchemy import update
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateField, TimeField
from wtforms.validators import DataRequired, Length, Optional

from . import main
from .. import db
from ..models import Reminder

from ..email import send_email

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
        
        send_email.delay(current_user.email, r.subject, r.content)

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

def print_hello():
    print('Hello')