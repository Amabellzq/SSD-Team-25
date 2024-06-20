import pymysql
from flask import current_app

def get_db_connection():
    return pymysql.connect(
        host=current_app.config['MYSQL_HOST'],
        user=current_app.config['MYSQL_ADMIN_USER'],
        password=current_app.config['MYSQL_ADMIN_PASSWORD'],
        database=current_app.config['MYSQL_DATABASE'],
        cursorclass=pymysql.cursors.DictCursor
    )
