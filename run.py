import os
from app import create_app, db

flask_app = create_app()
DATABASE_PATH = os.path.abspath(os.getcwd() + '/app/database.db')


if __name__ == '__main__':
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)

    db.create_all()
    flask_app.run(debug=True)
    