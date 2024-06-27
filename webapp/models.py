from flask_login import UserMixin
from .db import get_db_connection  # Ensure this import is correct
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# class User(UserMixin):
#     def __init__(self, user_data):
#         self.id = user_data['user_id']
#         self.username = user_data['username']
#         self.password = user_data['password']
#         self.role = user_data['role']

#     @staticmethod
#     def get(user_id):
#         try:
#             conn = get_db_connection()
#             with conn.cursor() as cursor:
#                 sql = "SELECT * FROM User WHERE user_id = %s"
#                 cursor.execute(sql, (user_id,))
#                 user = cursor.fetchone()
#             return User(user) if user else None
#         finally:
#             conn.close()
    
#     @staticmethod
#     def get_by_id(user_id):
#         return User.get(user_id)

# def load_user(user_id):
#     return User.get(user_id)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    @staticmethod
    def get(user_id):
        return User.query.get(user_id)

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

def load_user(user_id):
    return User.get(user_id)