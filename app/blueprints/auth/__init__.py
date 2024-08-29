from flask import Blueprint

# Create the auth blueprint
auth = Blueprint('auth', __name__, template_folder='templates')

# Import the routes module after defining the blueprint
from . import routes 
