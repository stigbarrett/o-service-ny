from flask import Blueprint

bp = Blueprint('tilmelding', __name__)

from app.tilmelding import routes