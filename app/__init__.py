import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap4
from flask_mail import Mail
from config import config
from celery import Celery
from redbeat import schedulers
from custom_enc_dec import CustomJSONDecoder, CustomJSONEncoder

celery = Celery(__name__)
mail = Mail()
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bootstrap = Bootstrap4()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    celery.conf.update(
        imports = app.config['CELERY_IMPORTS'],
        enable_utc = app.config['CELERY_ENABLE_UTC'],
        broker_url = app.config['CELERY_BROKER_URL'],
        redbeat_redis_url = app.config['REDBEAT_REDIS_URL'],
        redbeat_lock_timeout = 15
        )
    schedulers.RedBeatJSONDecoder = CustomJSONDecoder
    schedulers.RedBeatJSONEncoder = CustomJSONEncoder

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

    @app.cli.command("delete_versions")
    def delete_versions():
        db.session.execute(' DELETE FROM "alembic_version" ')
        db.session.commit()
    
    return app


