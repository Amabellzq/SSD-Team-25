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
    MYSQL_ADMIN_USER = os.getenv('MYSQL_ADMIN_USER')
    MYSQL_ADMIN_PASSWORD = os.getenv('MYSQL_ADMIN_PASSWORD')

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_ADMIN_USER}:{MYSQL_ADMIN_PASSWORD}"
        f"@{MYSQL_HOST}:3306/{MYSQL_DATABASE}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
