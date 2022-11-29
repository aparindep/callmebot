from flask import current_app, render_template
from flask_mail import Message
from callmebot import mail

def send_email(to, subject, html_body):
    msg = Message(current_app.config['MAIL_PREFIX'] + subject, sender=current_app.config['MAIL_ADMIN'], recipients=[to])
    msg.html = html_body
    with current_app.app_context():
        mail.send(msg)

