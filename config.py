from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

class Config:
    SECRET_KEY = environ.get('SECRET_KEY') or 'you cant guess'

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_ADMIN = environ.get('MAIL_ADMIN')
    MAIL_USERNAME = environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = environ.get('MAIL_PASSWORD')
    MAIL_PREFIX = '[Call Me Bot]'
    
    SQLALCHEMY_DATABASE_URI = 'postgresql:///callmebot'
    SQLALCHEMY_TRACK_MODIFICATION = False

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql:///'
    TESTING = True
    WTF_CSRF_ENABLED = False