from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap4
from flask_mail import Mail
from config import Config

mail = Mail()
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bootstrap = Bootstrap4()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from callmebot import models
    mail.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bootstrap.init_app(app)

    from callmebot.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from callmebot.main import main as main_bp
    app.register_blueprint(main_bp)

    return app



