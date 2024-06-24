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

# class User:
#     # Define users as a class attribute
#     # users = {
#     #     '1': {'id': '1', 'username': 'user1', 'email': 'user1@example.com', 'role': 'user', 'password': 'nugget'},
#     #     '2': {'id': '2', 'username': 'seller1', 'email': 'seller1@example.com', 'role': 'seller', 'password': 's3cr3t'},
#     #     '3': {'id': '3', 'username': 'admin', 'email': 'admin@example.com', 'role': 'admin', 'password': 'iamAdmin'},
#     # }

#     def __init__(self, id, username, email, role, password):
#         self.id = id
#         self.username = username
#         self.email = email
#         self.role = role
#         self.password = password

#     @classmethod
#     def get(cls, username):
#         for user_id, user in cls.users.items():
#             if user['username'] == username:
#                 return cls(**user)
#         return None
    
#     @classmethod
#     def get_by_id(cls, user_id):
#         user_dict = cls.users.get(user_id)
#         if user_dict:
#             return cls(**user_dict)
#         return None

#     def is_authenticated(self):
#         return True

#     def is_active(self):
#         return True

#     def is_anonymous(self):
#         return False

#     def get_id(self):
#         return self.id

# def load_user(user_id):
#     user_dict = User.users.get(user_id)
#     if user_dict:
#         return User(user_dict['id'], user_dict['username'], user_dict['email'], user_dict['role'], user_dict['password'])
#     return None

