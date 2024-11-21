from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, date, timedelta, time
from datetime import time as datetime_time

client = MongoClient('mongodb://localhost:27017/')
db = client['conference_room_booking']

class Booking:
    def __init__(self, user_id, room_id, date, start_time, end_time, id=None):
        self.id = str(id) if id else None
        self.user_id = user_id
        self.room_id = room_id
        self.date = self._parse_date(date)
        self.start_time = self._parse_time(start_time)
        self.end_time = self._parse_time(end_time)

    def to_dict(self):
        return {
            'id': self.id,
            'room_id': self.room_id,
            'room_name': self.room_name,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'date': self.date.isoformat() if isinstance(self.date, date) else self.date,
            'start_time': self.start_time.isoformat() if isinstance(self.start_time, datetime_time) else self.start_time,
            'end_time': self.end_time.isoformat() if isinstance(self.end_time, datetime_time) else self.end_time
        }

    @staticmethod
    def from_dict(data):
        return Booking(
            user_id=data['user_id'],
            room_id=data['room_id'],
            date=data['date'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            id=data.get('_id')
        )
        
    def save(self):
        booking_data = self.to_dict()
        if self.id:
            db.bookings.update_one({'_id': ObjectId(self.id)}, {'$set': booking_data})
        else:
            result = db.bookings.insert_one(booking_data)
            self.id = str(result.inserted_id)

    @staticmethod
    def _parse_date(date_val):
        if isinstance(date_val, str):
            try:
                return datetime.strptime(date_val, "%Y-%m-%d").date()
            except ValueError:
                return date_val
        elif isinstance(date_val, datetime):
            return date_val.date()
        elif isinstance(date_val, date):
            return date_val
        else:
            return str(date_val)

    @staticmethod
    def _parse_time(time_val):
        if isinstance(time_val, str):
            try:
                return datetime.strptime(time_val, "%H:%M").time()
            except ValueError:
                return time_val
        elif isinstance(time_val, datetime):
            return time_val.time()
        elif isinstance(time_val, time):
            return time_val
        else:
            return str(time_val)

    @staticmethod
    def get_all():
        bookings = db.bookings.find()
        return [Booking.from_dict(booking) for booking in bookings]

    @staticmethod
    def get_user_bookings(user_id):
        if user_id is None:
            print("Warning: get_user_bookings called with None user_id")
            return []
        
        print(f"Searching for bookings with user_id: {user_id}")
        bookings = list(db.bookings.find({'user_id': user_id}))
        print(f"Raw bookings from database: {bookings}")
        
        if not bookings:
            print("No bookings found for this user_id : ", user_id)
        
        result = [Booking.from_dict(booking) for booking in bookings if booking is not None]
        print(f"Processed bookings: {result}")
    
        return result
    
    @staticmethod
    def get_by_id(booking_id):
        booking = db.bookings.find_one({'_id': ObjectId(booking_id)})
        return Booking.from_dict(booking) if booking else None

    def delete(self):
        if self.id:
            db.bookings.delete_one({'_id': ObjectId(self.id)})

    @staticmethod
    def is_room_available(room_id, date, start_time, end_time):
        start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
        end_datetime = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")
        
        existing_bookings = db.bookings.find({
            'room_id': room_id,
            'date': date,
            '$or': [
                {'start_time': {'$lt': end_time}, 'end_time': {'$gt': start_time}},
                {'start_time': {'$gte': start_time, '$lt': end_time}},
                {'end_time': {'$gt': start_time, '$lte': end_time}}
            ]
        })
        
        return not any(existing_bookings)

    @staticmethod
    def get_booked_rooms(date, start_time, end_time):
        bookings = db.bookings.find({
            'date': date,
            '$or': [
                {'start_time': {'$lt': end_time}, 'end_time': {'$gt': start_time}},
                {'start_time': {'$gte': start_time, '$lt': end_time}},
                {'end_time': {'$gt': start_time, '$lte': end_time}}
            ]
        })
        return [booking['room_id'] for booking in bookings]

    @property
    def room_name(self):
        if self.room_id == 'all':
            return 'All Rooms'
        try:
            room = db.rooms.find_one({'_id': ObjectId(self.room_id)})
            return room['name'] if room else 'Unknown Room'
        except InvalidId:
            return 'Invalid Room'

    @property
    def user_name(self):
        try:
            user = db.users.find_one({'_id': ObjectId(self.user_id)})
            return user['name'] if user else 'Unknown User'
        except InvalidId:
            return 'Invalid User'
        
    @staticmethod
    def count_bookings(start_date, end_date=None):
        query = {'date': {'$gte': start_date.strftime('%Y-%m-%d')}}
        if end_date:
            query['date']['$lt'] = end_date.strftime('%Y-%m-%d')
        return db.bookings.count_documents(query)

    @staticmethod
    def get_booking_trends(start_date, end_date):
        pipeline = [
            {'$match': {'date': {'$gte': start_date.strftime('%Y-%m-%d'), '$lte': end_date.strftime('%Y-%m-%d')}}},
            {'$group': {'_id': '$date', 'count': {'$sum': 1}}},
            {'$sort': {'_id': 1}}
        ]
        results = list(db.bookings.aggregate(pipeline))
        dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range((end_date - start_date).days + 1)]
        counts = [next((r['count'] for r in results if r['_id'] == date), 0) for date in dates]
        return {'dates': dates, 'counts': counts}

    @staticmethod
    def get_room_usage(start_date, end_date):
        pipeline = [
            {'$match': {'date': {'$gte': start_date.strftime('%Y-%m-%d'), '$lt': end_date.strftime('%Y-%m-%d')}}},
            {'$group': {'_id': '$room_id', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        results = list(db.bookings.aggregate(pipeline))
        
        room_data = []
        for r in results:
            try:
                room = db.rooms.find_one({'_id': ObjectId(r['_id'])})
                if room:
                    room_data.append({
                        'name': room['name'],
                        'count': r['count']
                    })
            except InvalidId:
                continue
        
        room_names = [data['name'] for data in room_data]
        counts = [data['count'] for data in room_data]
        
        return {'rooms': room_names, 'counts': counts}

    @staticmethod
    def get_bookings(start_date, end_date):
        bookings = db.bookings.find({
            'date': {
                '$gte': start_date.strftime('%Y-%m-%d'),
                '$lte': end_date.strftime('%Y-%m-%d')
            }
        })
        return [Booking.from_dict(booking) for booking in bookings]
    
    @staticmethod
    def to_calendar_dict(booking):
        return {
            'id': str(booking['_id']),
            'title': f"{booking['room_name']} - {booking['user_name']}",
            'start': f"{booking['date']}T{booking['start_time']}",
            'end': f"{booking['date']}T{booking['end_time']}",
            'room_id': booking['room_id'],
            'user_id': booking['user_id']
        }