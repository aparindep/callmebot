from flask import Blueprint

main = Blueprint('main', __name__)

from callmebot.main import routes