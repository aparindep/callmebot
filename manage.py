from flask_script import Manager
from run import flask_app
from app import db

manager = Manager(flask_app)

@manager.command
def dropdb():
    db.drop_all()

