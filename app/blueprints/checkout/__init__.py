from flask import Blueprint

checkout = Blueprint('checkout', __name__, template_folder='templates')

from . import routes
