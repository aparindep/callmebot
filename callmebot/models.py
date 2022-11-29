from flask import render_template, current_app
from datetime import  datetime
from flask_login import UserMixin
from callmebot import db
from . import login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img_filename = db.Column(db.String(50))
    text = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow) # TODO: add time from now system
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    likes = db.relationship('Like')

    def to_json(self):
        json_post = {
            'id': self.id,
            'img_filename': self.img_filename,
            'text': self.text,
            'author_id': self.author_id,
            'html': render_template('post.html', post=self, author=User.query.filter_by(id=self.author_id).first())
        }
        return json_post

class Like(db.Model):
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    nickname = db.Column(db.String(64), default=False)
    posts = db.relationship("Post", backref='author')
    likes = db.relationship("Like")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


    def check_password(self, password):
        if check_password_hash(self.password_hash, password):
            return True

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
    
        if data['confirm'] != self.id:
            return False
        
        self.confirmed = True
        db.session.merge(self)
        db.session.commit()
        return True
        
