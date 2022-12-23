from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

class Config:
    SECRET_KEY = environ.get('SECRET_KEY') or 'you cant guess'

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_DEFAULT_SENDER = environ.get('MAIL_USERNAME')
    MAIL_USERNAME = environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = environ.get('MAIL_PASSWORD')
    MAIL_PREFIX = '[Call Me Bot]'
    
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CELERY_BROKER_URL = environ.get('CELERY_BROKER_URL')
    REDBEAT_REDIS_URL = environ.get('REDBEAT_REDIS_URL')
    CELERY_ENABLE_UTC = False

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql:///'
    TESTING = True
    WTF_CSRF_ENABLED = False

config = {
    'default': Config,
    'testing': TestingConfig
}