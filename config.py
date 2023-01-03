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
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CELERY_IMPORTS = ('app.email', )
    CELERY_ENABLE_UTC = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL')
    CELERY_BROKER_URL = environ.get('MY_CELERY_BROKER_URL')
    REDBEAT_REDIS_URL = environ.get('MY_CELERY_REDBEAT_REDIS_URL')
    
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql:///callmebot'
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    REDBEAT_REDIS_URL = 'redis://localhost:6379/1'

class TestingConfig(DevelopmentConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'postgresql:///'

config = {
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig
}