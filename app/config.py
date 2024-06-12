import os
from dotenv import load_dotenv


def load_secrets():
    secrets = [
        'secret_key',
        'mysql_root_password',
        'mysql_database',
        'mysql_admin_user',
        'mysql_admin_password',
        'mysql_merchant_user',
        'mysql_merchant_password',
        'mysql_user',
        'mysql_user_password',
        'mysql_readonly_user',
        'mysql_readonly_password',
        'mysql_host'
    ]

    for secret in secrets:
        secret_path = f'/run/secrets/{secret}'
        if os.path.exists(secret_path):
            with open(secret_path, 'r') as secret_file:
                os.environ[secret.upper()] = secret_file.read().strip()


# Load secrets if running in Docker, otherwise load from .env file
if os.path.exists('/run/secrets'):
    load_secrets()
else:
    load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SESSION_TYPE = os.getenv('SESSION_TYPE')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI_ADMIN = f"mysql+pymysql://{os.getenv('MYSQL_ADMIN_USER')}:{os.getenv('MYSQL_ADMIN_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DATABASE')}"
    SQLALCHEMY_DATABASE_URI_MERCHANT = f"mysql+pymysql://{os.getenv('MYSQL_MERCHANT_USER')}:{os.getenv('MYSQL_MERCHANT_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DATABASE')}"
    SQLALCHEMY_DATABASE_URI_USER = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_USER_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DATABASE')}"
    SQLALCHEMY_DATABASE_URI_READONLY = f"mysql+pymysql://{os.getenv('MYSQL_READONLY_USER')}:{os.getenv('MYSQL_READONLY_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DATABASE')}"
