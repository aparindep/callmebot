from flask import current_app
from flask_mail import Message
from . import mail, celery

@celery.task
def send_email(reminder_id, to, subject="", content=""):
    msg = Message(
        subject = current_app.config['MAIL_PREFIX'] + ' ' + subject,
        sender = current_app.config['MAIL_ADMIN'],
        recipients = [to]
        )   
    msg.html = content
    mail.send(msg)
    print(f'Sending email of remainder with id {reminder_id}')