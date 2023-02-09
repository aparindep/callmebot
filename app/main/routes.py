import datetime
import pytz
from functools import partial, wraps
from flask import redirect, render_template
from flask_login import login_required, current_user
from sqlalchemy import update
from celery import schedules
from redbeat import RedBeatSchedulerEntry
from . import main
from app import db, celery
from app.models import Reminder
from app.email import send_email
from app.main.forms import ReminderForm

def confirm_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.confirmed:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

@main.route('/', defaults={'page': None})
@main.route('/<int:page>', methods = ['GET'])
def index(page=1):
    if current_user.is_authenticated:
        if current_user.confirmed:
            per_page = 5
            query = Reminder.query.filter_by(author_id = current_user.id).order_by(Reminder.id.desc())
            reminders = query.paginate(page, per_page, error_out=False)
            return render_template('main/home.html', reminders=reminders)
        else:
            return render_template('main/confirm_required.html')
    else:
        return render_template('misc/welcome.html')

@main.route('/new/<reminder_type>', methods = ['GET', 'POST'])
@login_required
@confirm_required
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

        user_tz = pytz.timezone(current_user.timezone)
        
        if reminder_type == 'periodic':
            interval = schedules.crontab(
                minute = data['time'].minute,
                hour = data['time'].hour,
                day_of_week = list_to_string(data['days']),
                nowfun = partial(datetime.datetime.now, user_tz)
            )
            entry = RedBeatSchedulerEntry(
                name = str(r.id),
                task = 'app.email.send_email',
                schedule = interval,
                args = (current_user.email, r.subject, r.content),
                app = celery
            )
            entry.save()
        elif reminder_type == 'deadline':
            send_email.apply_async(
                task_id = str(r.id),
                args = (current_user.email, r.subject, r.content),
                eta = user_tz.localize(datetime.datetime.combine(r.date, r.time))
            )
        return redirect('/')
    return render_template('main/new.html', form=form, reminder_type=reminder_type)

@main.route('/edit/<reminder_id>', methods=['GET', 'POST'])
@login_required
@confirm_required
def edit(reminder_id):
    r = Reminder.query.filter_by(id = reminder_id).first()
    form = ReminderForm(
            subject = r.subject,
            content = r.content,
            date = r.date,
            days = r.days,
            time = r.time
            )
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
    return render_template('main/edit_reminder.html', form=form)

@main.route('/delete/<reminder_id>', methods=['POST'])
@login_required
@confirm_required
def delete(reminder_id):
    r = Reminder.query.filter_by(id = reminder_id).first()
    
    if r.days != None: # periodic reminder
        e = RedBeatSchedulerEntry.from_key(f'redbeat:{r.id}', app=celery)
        e.delete()
    elif r.date != None: # deadline reminder
        celery.control.revoke(str(r.id))
    
    db.session.delete(r)
    db.session.commit()
    
    return redirect('/')

@main.route('/about')
def about():
    return render_template('misc/about.html')

def list_to_string(li: list) -> str:
    """
    Converts a list of strings to a single string with commas inbetween values.
    Also converts each string from the list to lowercase.
    """ 
    str = li[0].lower()
    for i in range(1, len(li)):
        str += f',{li[i].lower()}'
    return str