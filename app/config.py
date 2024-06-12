import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SESSION_TYPE = os.getenv('SESSION_TYPE')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI_ADMIN = f"mysql+pymysql://{os.getenv('MYSQL_ADMIN_USER')}:{os.getenv('MYSQL_ADMIN_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DATABASE')}"
    SQLALCHEMY_DATABASE_URI_MERCHANT = f"mysql+pymysql://{os.getenv('MYSQL_MERCHANT_USER')}:{os.getenv('MYSQL_MERCHANT_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DATABASE')}"
    SQLALCHEMY_DATABASE_URI_USER = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_USER_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DATABASE')}"
    SQLALCHEMY_DATABASE_URI_READONLY = f"mysql+pymysql://{os.getenv('MYSQL_READONLY_USER')}:{os.getenv('MYSQL_READONLY_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DATABASE')}"
