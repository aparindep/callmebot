import os
from callmebot import db

DATABASE_PATH = os.path.abspath(os.getcwd() + '/callmebot/database.db')

if os.path.exists(DATABASE_PATH):
    os.remove(DATABASE_PATH)

db.create_all()