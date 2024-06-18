class User:
    # Define users as a class attribute
    users = {
        '1': {'id': '1', 'username': 'user1', 'email': 'user1@example.com', 'role': 'user', 'password': 'nugget'},
        '2': {'id': '2', 'username': 'seller1', 'email': 'seller1@example.com', 'role': 'seller', 'password': 's3cr3t'}
    }

    def __init__(self, id, username, email, role, password):
        self.id = id
        self.username = username
        self.email = email
        self.role = role
        self.password = password

    @classmethod
    def get(cls, username):
        for user_id, user in cls.users.items():
            if user['username'] == username:
                return cls(**user)
        return None
    
    @classmethod
    def get_by_id(cls, user_id):
        user_dict = cls.users.get(user_id)
        if user_dict:
            return cls(**user_dict)
        return None

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

def load_user(user_id):
    user_dict = User.users.get(user_id)
    if user_dict:
        return User(user_dict['id'], user_dict['username'], user_dict['email'], user_dict['role'], user_dict['password'])
    return None
