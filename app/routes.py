from flask import Blueprint, render_template, jsonify
from .db import get_db_connection

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('homepage.html')

@main.route('/db_check')
def db_check():
    connection = None
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()
            return jsonify({"status": "success", "database": db_name['DATABASE()']}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if connection:
            connection.close()
