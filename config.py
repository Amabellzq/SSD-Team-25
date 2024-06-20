from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


class Config:
    MYSQL_HOST = os.getenv('MYSQL_HOST')
    MYSQL_PORT = os.getenv('MYSQL_PORT')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
    MYSQL_ADMIN_USER = os.getenv('MYSQL_ADMIN_USER')
    MYSQL_ADMIN_PASSWORD = os.getenv('MYSQL_ADMIN_PASSWORD')
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_ADMIN_USER}:{MYSQL_ADMIN_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
