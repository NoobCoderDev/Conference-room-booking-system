from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId

client = MongoClient('mongodb://localhost:27017/')
db = client['conference_room_booking']

class Room:
    def __init__(self, name, capacity, facilities, id=None, _id=None):
        self.id = str(_id) if _id else str(id) if id else None
        self.name = name
        self.capacity = capacity
        self.facilities = facilities

    def save(self):
        if not self.id:
            result = db.rooms.insert_one(self.__dict__)
            self.id = str(result.inserted_id)
        else:
            db.rooms.update_one({'_id': ObjectId(self.id)}, {'$set': self.__dict__})

    @staticmethod
    def get_by_id(room_id):
        if room_id == 'all':
            return Room.get_all()
        try:
            room_data = db.rooms.find_one({'_id': ObjectId(room_id)})
            return Room(**room_data) if room_data else None
        except InvalidId:
            return None

    @staticmethod
    def get_by_ids(room_ids):
        if 'all' in room_ids:
            return Room.get_all()
        valid_ids = [id for id in room_ids if ObjectId.is_valid(id)]
        rooms = db.rooms.find({'_id': {'$in': [ObjectId(id) for id in valid_ids]}})
        return [Room(**room) for room in rooms]

    @staticmethod
    def get_all():
        rooms = db.rooms.find()
        return [Room(**room) for room in rooms]
    
    @staticmethod
    def count_rooms():
        return db.rooms.count_documents({})
    
    def delete(self):
        if self.id:
            try:
                db.rooms.delete_one({'_id': ObjectId(self.id)})
            except Exception as e:
                print(f"Error in Room.delete(): {str(e)}")  # For debugging
                raise
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'capacity': self.capacity,
            'facilities': self.facilities
        }

    @staticmethod
    def from_dict(data):
        return Room(
            name=data['name'],
            capacity=data['capacity'],
            facilities=data['facilities'],
            id=data.get('_id')
        )