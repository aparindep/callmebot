import datetime
import pytz
from functools import partial

from flask import redirect,render_template
from sqlalchemy import update
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateField, TimeField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Optional
from redbeat import RedBeatSchedulerEntry
from celery import schedules

from . import main
from .. import db
from ..models import Reminder

from ..email import send_email

class ReminderForm(FlaskForm):
    subject = StringField(label='Subject', description='What should be the mail subject?', validators=[Optional(), Length(1,50, 'Subject must have between 5 and 50 characters.')] )
    content = TextAreaField(label='Content', description='What should be the mail content?', validators=[Optional(), Length(1,700, 'Content must have between 1 and 200 characters.')])
    date = DateField(label='Date', description='Which day should the mail be sent?', validators=[DataRequired('A day is required.')])
    days = SelectMultipleField(label='In which days should I remind you?', validators=[DataRequired()])
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


        interval = schedules.crontab(
            minute = data['time'].minute,
            hour = data['time'].hour,
            day_of_week = list_to_string(),
            )
        entry = RedBeatSchedulerEntry(
            name = str(r.id),
            task = 'app.email.send_email',
            schedule = interval,
            nowfun = partial(datetime.now, tz=pytz.timezone('America/Argentina/Buenos_Aires'))
        )
        entry.save()

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

def list_to_string(li):
    str = li[0].lower()
    for i in range(1, len(li)):
        str += f",{str[i]}"
    return str