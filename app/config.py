import os
from dotenv import load_dotenv

# Load environment variables from .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '..', '.env'))


class Config:
    """Base configuration class for all environments."""

    # --- Flask Configuration ---
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)  # Secure secret key
    FLASK_APP = os.environ.get('FLASK_APP') or 'run.py'  # Entry point for the application
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'development'
    SESSION_COOKIE_SECURE = True  # Secure cookies in production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # --- Database Configuration ---
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable modification tracking (improves performance)

    # --- Application Settings ---
    PRODUCTS_PER_PAGE = 9             # Products to display per page
    ADMIN_PRODUCTS_PAGE = 20
    USERS_PER_PAGE = 10                # Users to display per page in admin
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max image upload size
    
    # --- Mail Configuration ---
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    # MAIL_PORT = int(os.environ.get('MAIL_PORT'))  
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # --- Contact Information ---
    ADMINS = ['your_email@example.com']  # Email addresses to receive errors
    ADDRESS = os.environ.get('ADDRESS') or '123 Main Street, Anytown, Nigeria'
    PHONE_NUMBER = os.environ.get('PHONE_NUMBER') or '+234 80 1234 5678'
    WHATSAPP_NUMBER = os.environ.get('WHATSAPP_NUMBER') or '+2348069082380'
    CONTACT_EMAIL = os.environ.get('CONTACT_EMAIL') or 'contact@nobecelectronics.com'
    
    # --- Twilio Configuration (for WhatsApp) ---
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')  # Make sure it's in E.164 format (e.g., 'whatsapp:+14155552671')

    # --- Social Media Links ---
    FACEBOOK_URL = os.environ.get('FACEBOOK_URL')
    TWITTER_URL = os.environ.get('TWITTER_URL')
    INSTAGRAM_URL = os.environ.get('INSTAGRAM_URL')
    WHATSAPP_URL = os.environ.get('WHATSAPP_URL')

    # --- Image Upload Settings ---
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', "webp"}

    # --- Logging Configuration ---
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')  # Log to standard output (console) instead of file


class DevelopmentConfig(Config):
    """Configuration for development environment."""
    DEBUG = True


class TestingConfig(Config):
    """Configuration for testing environment."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # In-memory database for testing


class ProductionConfig(Config):
    """Configuration for production environment."""
    DEBUG = False


# Dictionary to map environment names to configuration classes
config_classes = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
