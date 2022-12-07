import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap4
from flask_mail import Mail
from config import config
from celery import Celery

celery = Celery(__name__, broker = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379'))
mail = Mail()
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bootstrap = Bootstrap4()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    celery.conf.update(app.config)
    
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


