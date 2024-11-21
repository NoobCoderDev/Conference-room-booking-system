from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import Room, Booking, Admin, User
from datetime import datetime, timedelta, time
from bson import ObjectId

admin = Blueprint('admin', __name__)

@admin.route('/dashboard')
@login_required
def dashboard():
    if not isinstance(current_user, Admin):
        return redirect(url_for('user.dashboard'))

    rooms = Room.get_all()
    all_bookings = Booking.get_all()

    today = datetime.now().date()
    this_month = today.replace(day=1)
    next_month = (this_month + timedelta(days=32)).replace(day=1)

    try:
        stats = {
            'todays_bookings': Booking.count_bookings(today),
            'total_rooms': Room.count_rooms(),
            'total_users': User.count_users(),
            'bookings_this_month': Booking.count_bookings(this_month, next_month)
        }

        booking_trends = Booking.get_booking_trends(today - timedelta(days=7), today)
        room_usage = Booking.get_room_usage(this_month, next_month)
    except Exception as e:
        # Log the error
        print(f"Error in dashboard: {str(e)}")
        # Provide default values
        stats = {'todays_bookings': 0, 'total_rooms': 0, 'total_users': 0, 'bookings_this_month': 0}
        booking_trends = {'dates': [], 'counts': []}
        room_usage = {'rooms': [], 'counts': []}

    return render_template('admin/dashboard.html', rooms=rooms, all_bookings=all_bookings,
                           stats=stats, booking_trends=booking_trends, room_usage=room_usage)
    
@admin.route('/room_management')
@login_required
def room_management():
    if not isinstance(current_user, Admin):
        return redirect(url_for('user.dashboard'))
    rooms = Room.get_all()
    return render_template('admin/room_management.html', rooms=rooms)

@admin.route('/add_room', methods=['POST'])
@login_required
def add_room():
    if not isinstance(current_user, Admin):
        return jsonify({'error': 'Unauthorized'}), 403
    
    name = request.form['name']
    capacity = int(request.form['capacity'])
    facilities = request.form['facilities']
    
    room = Room(name, capacity, facilities)
    room.save()
    
    return jsonify({'success': True, 'message': 'Room added successfully'})

@admin.route('/edit_room/<room_id>', methods=['POST'])
@login_required
def edit_room(room_id):
    if not isinstance(current_user, Admin):
        return jsonify({'error': 'Unauthorized'}), 403
    
    room = Room.get_by_id(room_id)
    if not room:
        return jsonify({'error': 'Room not found'}), 404
    
    room.name = request.form['name']
    room.capacity = int(request.form['capacity'])
    room.facilities = request.form['facilities']
    room.save()
    
    return jsonify({'success': True, 'message': 'Room updated successfully'})

@admin.route('/delete_room/<room_id>', methods=['POST'])
@login_required
def delete_room(room_id):
    if not isinstance(current_user, Admin):
        return jsonify({'error': 'Unauthorized'}), 403
    try:
        room = Room.get_by_id(room_id)
        if not room:
            return jsonify({'error': 'Room not found'}), 404
        
        room.delete()
        return jsonify({'success': True, 'message': 'Room deleted successfully'})
    except Exception as e:
        print(f"Error deleting room: {str(e)}")  # For debugging
        return jsonify({'error': 'An error occurred while deleting the room'}), 500

@admin.route('/delete_booking/<booking_id>', methods=['POST'])
@login_required
def delete_booking(booking_id):
    if not isinstance(current_user, Admin):
        return redirect(url_for('user.dashboard'))
    
    booking = Booking.get_by_id(booking_id)
    if booking:
        booking.delete()
        flash('Booking deleted successfully', 'success')
    else:
        flash('Unable to delete booking', 'danger')
    return redirect(url_for('admin.dashboard'))

@admin.route('/api/bookings', methods=['GET', 'POST'])
@login_required
def api_bookings():
    if not isinstance(current_user, Admin):
        return jsonify({'error': 'Unauthorized'}), 403

    if request.method == 'GET':
        bookings = Booking.get_all()
        return jsonify([booking.to_dict() for booking in bookings])
    elif request.method == 'POST':
        data = request.json
        booking = Booking(
            user_id=data['user_id'],
            room_id=data['room_id'],
            date=data['date'],
            start_time=data['start_time'],
            end_time=data['end_time']
        )
        booking.save()
        return jsonify({'message': 'Booking created successfully'}), 201

@admin.route('/api/bookings/<booking_id>', methods=['DELETE'])
@login_required
def api_delete_booking(booking_id):
    if not isinstance(current_user, Admin):
        return jsonify({'error': 'Unauthorized'}), 403

    booking = Booking.get_by_id(booking_id)
    if booking:
        booking.delete()
        return jsonify({'message': 'Booking deleted successfully'}), 200
    return jsonify({'error': 'Booking not found'}), 404

@admin.route('/user_management')
@login_required
def user_management():
    # Fetch all users
    users = list(User.get_all_users())
    total_users = len(users)

    # # Calculate active users (users who logged in within the last 30 days)
    # thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    # active_users = sum(1 for user in users if user.get('last_login', datetime.min) > thirty_days_ago)

    # # Calculate new users this month
    # new_users_this_month = sum(1 for user in users if user.get('registration_date', datetime.min) > thirty_days_ago)

    # # Calculate average bookings per user
    # total_bookings = len(Booking.get_all())
    # avg_bookings_per_user = round(total_bookings / total_users, 2) if total_users > 0 else 0

    active_users = 3;
    new_users_this_month = 3;
    avg_bookings_per_user = 10; 
    
    user_stats = {
        'total_users': total_users,
        'active_users': active_users,
        'new_users_this_month': new_users_this_month,
        'avg_bookings_per_user': avg_bookings_per_user
    }

    # # Add total bookings for each user
    # for user in users:
    #     user['total_bookings'] = Booking.get_user_bookings_count(str(user['_id']))

    return render_template('admin/user_management.html', users=users, total_bookings=10, user_stats=user_stats)

@admin.route('/get_user_bookings/<user_id>')
@login_required
def get_user_bookings(user_id):
    try:
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({'error': "User not found"}), 404
        
        bookings = Booking.get_user_bookings(user_id)
        print("Devanshu : ", bookings)
        return jsonify({
            'bookings': [
                {
                    'room_name': booking.room_name,
                    'date': booking.date.strftime('%Y-%m-%d') if isinstance(booking.date, datetime) else booking.date,
                    'start_time': booking.start_time.strftime('%H:%M') if isinstance(booking.start_time, time) else booking.start_time,
                    'end_time': booking.end_time.strftime('%H:%M') if isinstance(booking.end_time, time) else booking.end_time
                } for booking in bookings
            ]
        })
    except Exception as e:
        print(f"Error in get_user_bookings: {str(e)}")  # Log the error
        return jsonify({'error': "Internal server error."}), 500

# Error handlers
@admin.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404