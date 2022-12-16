from flask import Blueprint

bp = Blueprint('resultater', __name__)

from app.resultater import routes