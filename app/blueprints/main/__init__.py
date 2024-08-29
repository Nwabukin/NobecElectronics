from flask import Blueprint

# Create the main blueprint
main = Blueprint('main', __name__, template_folder='templates', static_folder='static')

# Import the routes module (deferred import)
from . import routes
