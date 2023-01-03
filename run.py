import os
from app import create_app

flask_app = create_app(os.getenv('FLASK_CONFIG'))

if __name__ == '__main__':
    flask_app.run()
    