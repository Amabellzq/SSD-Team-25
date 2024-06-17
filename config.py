from dotenv import load_dotenv
import os

load_dotenv()

MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
MYSQL_ADMIN_USER = os.getenv('MYSQL_ADMIN_USER')
MYSQL_ADMIN_PASSWORD = os.getenv('MYSQL_ADMIN_PASSWORD')
