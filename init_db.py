import os
from app import db

DATABASE_PATH = os.path.abspath(os.getcwd() + '/app/database.db')

if os.path.exists(DATABASE_PATH):
    os.remove(DATABASE_PATH)

db.create_all()