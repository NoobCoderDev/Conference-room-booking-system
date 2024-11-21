from .user import User, db
from bson import ObjectId

class Admin(User):
    def __init__(self, name, email, password=None, id=None, _id=None, password_hash=None, **kwargs):
        super().__init__(name, email, password, id=id, _id=_id, password_hash=password_hash, **kwargs)
        self.is_admin = True
        
    def save(self):
        # Ensure is_admin is always True for Admin instances
        self.is_admin = True
        super().save()

    @staticmethod
    def get_by_id(user_id):
        user_data = db.users.find_one({'_id': ObjectId(user_id), 'is_admin': True})
        if user_data:
            return Admin(**user_data)
        return None

    @staticmethod
    def get_by_email(email):
        user_data = db.users.find_one({'email': email, 'is_admin': True})
        if user_data:
            return Admin(**user_data)
        return None