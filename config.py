from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Config:
    # Database configuration with proper variable names
    MYSQL_HOST = os.getenv('MYSQL_HOST')  # Default to localhost
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
    MYSQL_USER = os.getenv('MYSQL_USER')  # Non-root user for the application
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')

    # URL-encode the username and password for safety
    MYSQL_USER_ENCODED = quote_plus(MYSQL_USER)
    MYSQL_PASSWORD_ENCODED = quote_plus(MYSQL_PASSWORD)

    # SQLAlchemy Database URI
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER_ENCODED}:{MYSQL_PASSWORD_ENCODED}"
        f"@{MYSQL_HOST}:3306/{MYSQL_DATABASE}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use an in-memory SQLite database for testing
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SERVER_NAME = 'localhost'  # Required for URL generation in tests
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing purposes
    APPLICATION_ROOT = '/'  # Optional
    PREFERRED_URL_SCHEME = 'http'  # Changed from https to http for local testing
