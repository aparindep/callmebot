import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateField, TimeField, SelectMultipleField, ValidationError
from wtforms.validators import DataRequired, Length, Optional

def DaysRequired(form, field):
    if not field.data and not form.data['date']:
        raise ValidationError('Please select on what days of the week I should email you.')

def DateRequired(form, field):
    if not field.data and not form.data['days']:
        raise ValidationError('Please select when I should email you.')
    
class ReminderForm(FlaskForm):
    subject = StringField(label='Subject', description='What should be the mail subject?', validators=[DataRequired(), Length(1,50, 'Subject must have between 5 and 50 characters.')] )
    content = TextAreaField(label='Content', description='What should be the mail content?', validators=[Optional(), Length(1,700, 'Content must have between 1 and 200 characters.')])
    days = SelectMultipleField(label='Days', description='What days of the week should I email you?', validators=[DaysRequired], choices = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'], render_kw = {'class': 'days-select'},  default = None)
    date = DateField(label='Date', validators=[DateRequired], description='When should I email you?', default = None)
    time = TimeField(label='Time', description='What time should I email you? Use 24-hour clock notation, e.g. 08:15 or 23:45).', validators=[DataRequired('A time is required.')], default=datetime.time(0,0))
    submit = SubmitField('Submit')
    