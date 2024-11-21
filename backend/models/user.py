from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from flask_login import UserMixin
from datetime import datetime

# Assuming you have a MongoDB connection established
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['conference_room_booking']  # Replace with your actual database name

class User(UserMixin):
    def __init__(self, name, email, password=None, is_admin=False, id=None, _id=None, password_hash=None, created_at=None, **kwargs):
        self.id = str(_id) if _id else str(id) if id else None
        self.name = name
        self.email = email
        if password:
            self.password_hash = generate_password_hash(password)
        elif password_hash:
            self.password_hash = password_hash
        else:
            self.password_hash = None
        self.is_admin = is_admin
        self.created_at = created_at if created_at else datetime.utcnow()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def save(self):
        user_data = {
            'name': self.name,
            'email': self.email,
            'password_hash': self.password_hash,
            'is_admin': self.is_admin,
            'created_at': self.created_at
        }
        if self.id:
            db.users.update_one({'_id': ObjectId(self.id)}, {'$set': user_data})
        else:
            result = db.users.insert_one(user_data)
            self.id = str(result.inserted_id)
            return result
            
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    @staticmethod
    def get_by_email(email):
        user_data = db.users.find_one({'email': email})
        if user_data:
            from .admin import Admin  # Import here to avoid circular import
            if user_data.get('is_admin', False):
                return Admin(**user_data)
            return User(**user_data)
        return None
    
    @staticmethod
    def get_by_name(name):
        user_data = db.users.find_one({'name': name})
        if user_data:
            from .admin import Admin  # Import here to avoid circular import
            if user_data.get('is_admin', False):
                return Admin(**user_data)
            return User(**user_data)
        return None

    @staticmethod
    def get_by_id(user_id):
        user_data = db.users.find_one({'_id': ObjectId(user_id)})
        if user_data:
            from .admin import Admin  # Import here to avoid circular import
            if user_data.get('is_admin', False):
                return Admin(**user_data)
            return User(**user_data)
        return None
    
    @staticmethod
    def count_users():
        return db.users.count_documents({})
    
    @staticmethod
    def get_all_users():
        return db.users.find()
    
    @staticmethod
    def get_user_bookings_count(user_id):
        return db.bookings.count_documents({'user_id': user_id})