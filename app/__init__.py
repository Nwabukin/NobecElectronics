import os
import hashlib
import logging
from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

from .config import config_classes, Config

# Initialize Flask extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

# Set up login manager
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

UPLOAD_FOLDER = 'app/static/uploads/profile_pics'  


def create_app(config_name='development'):
    """Factory function to create the Flask app."""

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_classes[config_name])
    
    # Load instance configuration (if it exists)
    if os.path.exists(os.path.join(app.instance_path, 'config.py')):
        app.config.from_pyfile('config.py')
        
    # set UPLOAD_FOLDER after app.config is updated
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    # Function for versioned static files (for cache busting)
    def versioned_static(filename):
        """
        Generate a versioned URL for static files based on their content hash.
        """

        # Construct the full path to the static file
        file_path = os.path.join(app.static_folder, filename)

        try:
            # Calculate the MD5 hash of the file's content
            with open(file_path, "rb") as f:
                file_hash = hashlib.md5(f.read()).hexdigest()[:8]  # Take first 8 characters for shorter query string
        except FileNotFoundError:
            # Handle the case where the file doesn't exist
            app.logger.error(f"Static file not found: {filename}")
            return url_for("static", filename=filename)  # Fallback to unversioned URL

        # Append the hash as a query parameter to the URL
        return url_for("static", filename=filename) + "?v=" + file_hash

   
    app.jinja_env.globals['versioned_static'] = versioned_static


    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
   
    # Import models after app initialization
    from app.models import User
    
    # Import and Register Blueprints (Deferred Imports)
    from app.blueprints.main import main
    from app.blueprints.auth import auth
    from app.blueprints.products import products
    from app.blueprints.cart import cart
    from app.blueprints.checkout import checkout
    from app.blueprints.admin import admin

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(products, url_prefix='/products')
    app.register_blueprint(cart, url_prefix='/cart')  
    app.register_blueprint(checkout, url_prefix='/checkout')
    print("Checkout blueprint registered")
    app.register_blueprint(admin, url_prefix='/admin')

    # User loader for Flask-Login (Deferred Import)
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Logging configuration
    if app.config['LOG_TO_STDOUT']:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
    else:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = logging.FileHandler('logs/nobec.log')
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Nobec Electronics startup')

    # Error handling
    # with app.app_context():
    #     from app.errors import page_not_found, internal_server_error
    #     app.register_error_handler(404, page_not_found)
    #     app.register_error_handler(500, internal_server_error)


    return app


