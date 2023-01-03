from flask_script import Manager
from run import flask_app
from app import db

manager = Manager(flask_app)

@manager.command
def drop_versions():
    print('Dropping Alembic versions')
    db.session.execute(""" DELETE FROM "alembic_version" """)
    db.session.commit()

if __name__=='__main__':
    manager.run()