from math import floor
from pickletools import optimize
from re import I
from turtle import pos
from flask import get_flashed_messages, redirect, jsonify,render_template, abort, flash
from sqlalchemy import desc
from werkzeug.utils import secure_filename
from pathlib import Path
from PIL import Image

from . import main
from callmebot.models import Post, User, Like
from callmebot import db

from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateField, TimeField
from wtforms.validators import DataRequired, Length, Optional
import os



UPLOAD_FOLDER = os.path.abspath(os.getcwd()) + '/callmebot/static/images'

class ReminderForm(FlaskForm):
    subject = StringField(label='Subject', description='What should be the mail subject?', validators=[Optional(), Length(1,50, 'Subject must have between 5 and 50 characters.')] )
    content = TextAreaField(label='Content', description='What should be the mail content?', validators=[Optional(), Length(1,700, 'Content must have between 1 and 200 characters.')])
    date = DateField(label='Date', description='Which day should the mail be sent?', validators=[DataRequired('A day is required.')])
    time = TimeField(label='Time', description='What time should the mail be sent?', validators=[DataRequired('A time is required.')])
    submit = SubmitField('Add')

@main.route('/')
def index():
    return render_template('home.html')

@login_required
@main.route('/new', methods = ['GET', 'POST'])
def upload():
    form = ReminderForm()
    if form.validate_on_submit():
        print(form.data)
    return render_template('new.html', form=form)

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    
    print(user.posts)
    return render_template('user.html', user=user)

@main.route('/posts')
def get_posts():
    posts = Post.query.all()
    return jsonify({'posts': [post.to_json() for post in posts]})

@main.route('/posts/<username>')
def get_posts_by_username(username):
    author = User.query.filter_by(username = username).first()
    posts = Post.query.filter_by(author_id = author.id)
    return jsonify({'posts': [post.to_json() for post in posts]})

@main.route('/like/<post_id>', methods=['POST'])
def like(post_id):
    like_query = Like.query.filter(Like.author_id == current_user.id, Like.post_id == post_id)
    like_count = len(Post.query.filter_by(id = post_id).first().likes)
    if like_query.first():

        like_query.delete()
        db.session.commit()

        response = jsonify({'success': False, 'likeCount': like_count - 1})
        return response
    else:
        like = Like(author_id = current_user.id, post_id = post_id)
        db.session.add(like)
        db.session.commit()
        
        response = jsonify({'success': True, 'likeCount': like_count + 1})
        response.status_code = 200
        return response

from uuid import uuid4
def make_unique(string):
    ident = uuid4().__str__()
    return f'{ident}{Path(string).suffix}'