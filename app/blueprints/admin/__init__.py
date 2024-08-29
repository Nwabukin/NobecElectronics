from flask import Blueprint

admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

# Import routes modules after defining the blueprint
from . import category, product, user_order
