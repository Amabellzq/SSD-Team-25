# from flask import Blueprint, render_template
#
# main = Blueprint('main', __name__)
#
# @main.route('/')
# def home():
#     return render_template('homepage.html')

from flask import Blueprint, render_template
import pymysql
import os

main = Blueprint('main', __name__)


@main.route('/')
def home():
    return render_template('homepage.html')

@main.route('/db_check')
def db_check():
    connection = None
    try:
        connection = pymysql.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_ADMIN_USER'),
            password=os.getenv('MYSQL_ADMIN_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE'),
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()
            return f"Connected to database: {db_name['DATABASE()']}"
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        if connection:
            connection.close()
