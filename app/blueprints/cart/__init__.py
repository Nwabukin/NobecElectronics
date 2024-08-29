from flask import Blueprint

cart = Blueprint("cart", __name__, template_folder="templates")

# Import the routes module after defining the blueprint
from . import routes
