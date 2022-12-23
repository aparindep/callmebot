from flask import current_app
from flask_mail import Message
from . import mail, celery

@celery.task
def send_email(to, subject="", content="", **kwargs):
    msg = Message(
        subject = current_app.config['MAIL_PREFIX'] + ' ' + subject,
        recipients = [to]
        )   
    msg.html = content
    mail.send(msg)
    
    reminder_id = kwargs.get('reminder_id')
    if reminder_id:
        print(f'Sending email of remainder with id {reminder_id}')