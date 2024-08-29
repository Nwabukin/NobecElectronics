from app import create_app, db  # Import the create_app function and the db object
from app.config import Config
import os

# Get the configuration name from the environment variable (defaults to 'development')
config_name = os.environ.get('FLASK_ENV') or 'development'

# Create the Flask app instance
app = create_app(config_name)

# Create database tables if they don't exist
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()  # You can add host='0.0.0.0' to make it accessible on your network
