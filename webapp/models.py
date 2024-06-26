from flask_login import UserMixin
from .db import get_db_connection  # Ensure this import is correct

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['user_id']
        self.username = user_data['username']
        self.password = user_data['password']
        self.role = user_data['role']

    @staticmethod
    def get(user_id):
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                sql = "SELECT * FROM User WHERE user_id = %s"
                cursor.execute(sql, (user_id,))
                user = cursor.fetchone()
            return User(user) if user else None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(user_id):
        return User.get(user_id)

def load_user(user_id):
    return User.get(user_id)