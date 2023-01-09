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
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL')
    
    CELERY_BROKER_URL='redis://redis:6379/0'
    REDBEAT_REDIS_URL='redis://redis:6379/1'  
    CELERY_IMPORTS = ('app.email', )
    CELERY_ENABLE_UTC = False

class ProductionConfig(Config):
    FLASK_ENV = 'production'
    
class DevelopmentConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True

class TestingConfig(Config):
    FLASK_ENV = 'development'
    SQLALCHEMY_DATABASE_URI = environ.get('TEST_DATABASE_URL')
    WTF_CSRF_ENABLED = False

config = {
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig
}