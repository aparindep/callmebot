import datetime
import pytz
from functools import partial

from flask import redirect,render_template
from sqlalchemy import update
from celery import schedules
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateField, TimeField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Optional
from redbeat import RedBeatSchedulerEntry

from . import main
from .. import db, celery
from ..models import Reminder

class ReminderForm(FlaskForm):
    subject = StringField(label='Subject', description='What should be the mail subject?', validators=[Optional(), Length(1,50, 'Subject must have between 5 and 50 characters.')] )
    content = TextAreaField(label='Content', description='What should be the mail content?', validators=[Optional(), Length(1,700, 'Content must have between 1 and 200 characters.')])
    days = SelectMultipleField(label='Days', description='What days of the week should I email you?', validators=[Optional()], choices = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'], default = None)
    date = DateField(label='Date', description='When should I email you?', validators=[Optional()], default = None)
    time = TimeField(label='Time', description='What time should I email you?', validators=[DataRequired('A time is required.')], default=datetime.time(0,0))
    submit = SubmitField('Submit')

@main.route('/')
def index():
    if current_user.is_authenticated:
        reminders = Reminder.query.filter_by(author_id = current_user.id).all()
        return render_template('home.html', reminders = reminders)
    else:
        return redirect('/auth/register')

@main.route('/new/<reminder_type>', methods = ['GET', 'POST'])
@login_required
def new(reminder_type):
    form = ReminderForm()
    if form.validate_on_submit():
        data = form.data
        r = Reminder(
            subject=data['subject'],
            content=data['content'],
            time=data['time'],
            author_id=current_user.id
            )
        if (reminder_type == 'deadline'):
            r.date = data['date']
        elif (reminder_type == 'periodic'):
            r.days = data['days']

        db.session.add(r)
        db.session.commit()

        if reminder_type == 'periodic':
            interval = schedules.crontab(
                minute = data['time'].minute,
                hour = data['time'].hour,
                day_of_week = list_to_string(data['days']),
                nowfun = partial(datetime.datetime.now, pytz.timezone('America/Argentina/Buenos_Aires'))
                # TODO: add user timezone as column. ask for it in register page
            )
            entry = RedBeatSchedulerEntry(
                name = str(r.id),
                task = 'app.email.send_email',
                schedule = interval,
                args = (r.id, current_user.email, r.subject, r.content),
                app = celery
            )
            entry.save()
        # TODO: save entry key as database column

        return redirect('/')
        
    return render_template('new.html', form=form, reminder_type=reminder_type)

@main.route('/edit/<reminder_id>', methods=['GET', 'POST'])
def edit(reminder_id):
    r = Reminder.query.filter_by(id = reminder_id).first()
    form = ReminderForm(
            subject = r.subject,
            content = r.content,
            date = r.date,
            days = r.days,
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


def list_to_string(li: list) -> str:
    """
    Converts a list of strings to a single string with commas inbetween values.
    Also converts each string from the list to lowercase.
    """ 
    str = li[0].lower()
    for i in range(1, len(li)):
        str += f',{li[i].lower()}'
    return str
