import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap4
from flask_mail import Mail
from celery import Celery
from redbeat import schedulers
from custom_enc_dec import CustomJSONDecoder, CustomJSONEncoder
from config import config

celery = Celery(__name__)
mail = Mail()
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bootstrap = Bootstrap4()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config[os.getenv('APP_ENV')])
    celery.conf.update(
        imports = app.config['CELERY_IMPORTS'],
        enable_utc = app.config['CELERY_ENABLE_UTC'],
        broker_url = app.config['CELERY_BROKER_URL'],
        redbeat_redis_url = app.config['REDBEAT_REDIS_URL'],
        redbeat_lock_timeout = 15
        )
    schedulers.RedBeatJSONDecoder = CustomJSONDecoder
    schedulers.RedBeatJSONEncoder = CustomJSONEncoder

    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    from . import models

    mail.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bootstrap.init_app(app)

    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from .main import main as main_bp
    app.register_blueprint(main_bp)
    
    return app


