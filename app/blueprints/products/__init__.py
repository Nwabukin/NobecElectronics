from flask import Blueprint

# Create the products blueprint
products = Blueprint('products', __name__, template_folder='templates', static_folder='static')

# Import the routes module after defining the blueprint (to avoid circular imports)
from . import routes
