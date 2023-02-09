from flask import current_app, render_template
from flask_mail import Message
from . import mail, celery

@celery.task
def send_email(to, subject="", content=""):
    msg = Message(
        subject = current_app.config['MAIL_PREFIX'] + ' ' + subject,
        recipients = [to]
        )   
    msg.html = content
    mail.send(msg)

def send_password_reset_email(user):
    token = user.generate_password_reset_token()

    send_email(
        to=user.email,
        subject='Reset your password',
        recipients=user.email,
        content = render_template('email/reset_password.html',user=user, token=token)
    )
