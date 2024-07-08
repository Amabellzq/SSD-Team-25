from urllib.parse import quote_plus
from dotenv import load_dotenv
import os
# is to to avoid circular imports
from webapp import routes

# Load environment variables from .env file
load_dotenv()


class Config:
    # SECRET_KEY = os.getenv('SECRET_KEY', 'ssdT25')
    MYSQL_HOST = os.getenv('MYSQL_HOST')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
    # Admin user configuration
    MYSQL_ADMIN_USER = os.getenv('MYSQL_ADMIN_USER')
    MYSQL_ADMIN_PASSWORD = os.getenv('MYSQL_ADMIN_PASSWORD')
    MYSQL_ADMIN_USER_ENCODED = quote_plus(MYSQL_ADMIN_USER)
    MYSQL_ADMIN_PASSWORD_ENCODED = quote_plus(MYSQL_ADMIN_PASSWORD)
    SQLALCHEMY_ADMIN_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_ADMIN_USER_ENCODED}:{MYSQL_ADMIN_PASSWORD_ENCODED}"
        f"@{MYSQL_HOST}:3306/{MYSQL_DATABASE}"
    )

    # Merchant user configuration
    MYSQL_MERCHANT_USER = os.getenv('MYSQL_MERCHANT_USER')
    MYSQL_MERCHANT_PASSWORD = os.getenv('MYSQL_MERCHANT_PASSWORD')
    MYSQL_MERCHANT_USER_ENCODED = quote_plus(MYSQL_MERCHANT_USER)
    MYSQL_MERCHANT_PASSWORD_ENCODED = quote_plus(MYSQL_MERCHANT_PASSWORD)
    SQLALCHEMY_MERCHANT_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_MERCHANT_USER_ENCODED}:{MYSQL_MERCHANT_PASSWORD_ENCODED}"
        f"@{MYSQL_HOST}:3306/{MYSQL_DATABASE}"
    )

    # Regular user configuration
    MYSQL_USER = os.getenv('MYSQL_USER')
    MYSQL_USER_PASSWORD = os.getenv('MYSQL_USER_PASSWORD')
    MYSQL_USER_ENCODED = quote_plus(MYSQL_USER)
    MYSQL_USER_PASSWORD_ENCODED = quote_plus(MYSQL_USER_PASSWORD)
    SQLALCHEMY_USER_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER_ENCODED}:{MYSQL_USER_PASSWORD_ENCODED}"
        f"@{MYSQL_HOST}:3306/{MYSQL_DATABASE}"
    )

    # Readonly user configuration
    MYSQL_READONLY_USER = os.getenv('MYSQL_READONLY_USER')
    MYSQL_READONLY_PASSWORD = os.getenv('MYSQL_READONLY_PASSWORD')
    MYSQL_READONLY_USER_ENCODED = quote_plus(MYSQL_READONLY_USER)
    MYSQL_READONLY_PASSWORD_ENCODED = quote_plus(MYSQL_READONLY_PASSWORD)
    SQLALCHEMY_READONLY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_READONLY_USER_ENCODED}:{MYSQL_READONLY_PASSWORD_ENCODED}"
        f"@{MYSQL_HOST}:3306/{MYSQL_DATABASE}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY')


class TestConfig():
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use an in-memory SQLite database for testing
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SERVER_NAME = 'localhost'  # Required for URL generation
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing purposes
    APPLICATION_ROOT = '/'  # Optional
    PREFERRED_URL_SCHEME = 'https'  # Optional

