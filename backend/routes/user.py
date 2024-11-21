from flask import Blueprint, render_template, request, jsonify, redirect, url_for, Response
from flask_login import login_required, current_user
from models import Room, Booking
from datetime import datetime, date, timedelta
from datetime import time as datetime_time
import json
import time
import logging

user = Blueprint('user', __name__)

@user.route('/dashboard')
@login_required
def dashboard():
    rooms = Room.get_all()
    return render_template('user/dashboard.html', rooms=rooms)

@user.route('/api/bookings')
@login_required
def get_all_bookings():  # Changed function name
    bookings = Booking.get_all()
    return jsonify([booking.to_dict() for booking in bookings])

@user.route('/book_room', methods=['POST'])
@login_required
def book_room():
    room_id = request.form['room_id']
    booking_date = request.form['date']
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    
    # Convert string inputs to datetime objects
    booking_datetime = datetime.strptime(f"{booking_date} {start_time}", "%Y-%m-%d %H:%M")
    end_datetime = datetime.strptime(f"{booking_date} {end_time}", "%Y-%m-%d %H:%M")
    current_datetime = datetime.now()

    # Check if booking date is today and start time is in the past
    if booking_datetime.date() == date.today() and booking_datetime < current_datetime:
        return jsonify({'success': False, 'error': 'Start time cannot be in the past'}), 400

    # Check if end time is before start time
    if end_time <= start_time:
        return jsonify({'success': False, 'message': 'End time must be after start time'}), 400

    # Check if booking is for a future date
    if booking_datetime.date() < date.today():
        return jsonify({'success': False, 'error': 'Cannot book for a past date'}), 400

    # If all checks pass, create and save the booking
    try:
        booking = Booking(current_user.id, room_id, booking_date, start_time, end_time)
        booking.save()
        return jsonify({'message': 'Room booked successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user.route('/delete_booking/<booking_id>', methods=['POST'])
@login_required
def delete_booking(booking_id):
    booking = Booking.get_by_id(booking_id)
    if booking and booking.user_id == current_user.id:
        booking.delete()
        return jsonify({'message': 'Booking cancelled successfully'})
    return jsonify({'error': 'Unable to cancel booking'}, 400)

@user.route('/get_user_bookings')
@login_required
def get_user_bookings():
    now = datetime.now()
    all_bookings = Booking.get_user_bookings(str(current_user.id))
    
    active_bookings = []
    upcoming_bookings = []
    past_bookings = []

    for booking in all_bookings:
        try:
            booking_dict = booking.to_dict()
            
            # Parse date
            if isinstance(booking.date, str):
                booking_date = datetime.strptime(booking.date, "%Y-%m-%d").date()
            elif isinstance(booking.date, date):
                booking_date = booking.date
            else:
                raise ValueError(f"Unexpected date type: {type(booking.date)}")

            # Parse start time
            if isinstance(booking.start_time, str):
                booking_start_time = datetime.strptime(booking.start_time, "%H:%M:%S").time()
            elif isinstance(booking.start_time, datetime_time):
                booking_start_time = booking.start_time
            else:
                raise ValueError(f"Unexpected start_time type: {type(booking.start_time)}")

            # Parse end time
            if isinstance(booking.end_time, str):
                booking_end_time = datetime.strptime(booking.end_time, "%H:%M:%S").time()
            elif isinstance(booking.end_time, datetime_time):
                booking_end_time = booking.end_time
            else:
                raise ValueError(f"Unexpected end_time type: {type(booking.end_time)}")

            # Combine date and time for easier comparison
            booking_start = datetime.combine(booking_date, booking_start_time)
            booking_end = datetime.combine(booking_date, booking_end_time)

            # Handle bookings that end on the next day
            if booking_end < booking_start:
                booking_end += timedelta(days=1)

            if booking_start <= now < booking_end:
                active_bookings.append(booking_dict)
            elif now < booking_start:
                upcoming_bookings.append(booking_dict)
            else:
                past_bookings.append(booking_dict)

        except Exception as e:
            logging.error(f"Error processing booking: {e}")
            logging.error(f"Booking data: {booking.__dict__}")
            # Continue to the next booking instead of breaking the loop

    # Sort the bookings
    active_bookings.sort(key=lambda x: x['start_time'])
    upcoming_bookings.sort(key=lambda x: (x['date'], x['start_time']))
    past_bookings.sort(key=lambda x: (x['date'], x['start_time']), reverse=True)

    logging.info(f"Active bookings: {active_bookings}")
    logging.info(f"Upcoming bookings: {upcoming_bookings}")
    logging.info(f"Past bookings: {past_bookings}")

    print("Upcoming : ", upcoming_bookings)
    return jsonify({
        'active_bookings': active_bookings,
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings
    })
    
@user.route('/available_rooms')
@login_required
def available_rooms():
    try:
        date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        start_time = request.args.get('start_time', '09:00')
        end_time = request.args.get('end_time', '17:00')

        all_rooms = Room.get_all()
        booked_rooms = Booking.get_booked_rooms(date, start_time, end_time)
        available_rooms = [room for room in all_rooms if room.id not in booked_rooms]

        return render_template('user/available_rooms.html', rooms=available_rooms, date=date, start_time=start_time, end_time=end_time)
    except Exception as e:
        print(f"Error in available_rooms: {str(e)}")
        return jsonify({'error': 'An error occurred while fetching available rooms'}), 500

@user.errorhandler(401)
def unauthorized(error):
    return redirect(url_for('auth.login'))

@user.route('/booking-updates')
@login_required
def booking_updates():
    def generate():
        while True:
            # Get all bookings
            all_bookings = Booking.get_all()
            
            # Get user's bookings
            user_bookings = Booking.get_user_bookings(current_user.id)
            
            # Categorize user's bookings
            now = datetime.now()
            active_bookings = []
            upcoming_bookings = []
            past_bookings = []
            
            for booking in user_bookings:
                booking_start = datetime.combine(booking.date, datetime.strptime(booking.start_time, "%H:%M").time())
                booking_end = datetime.combine(booking.date, datetime.strptime(booking.end_time, "%H:%M").time())
                
                if booking_start <= now < booking_end:
                    active_bookings.append(booking.to_dict())
                elif now < booking_start:
                    upcoming_bookings.append(booking.to_dict())
                else:
                    past_bookings.append(booking.to_dict())
            
            # Prepare data for FullCalendar
            calendar_events = []
            for booking in all_bookings:
                is_user_booking = booking.user_id == current_user.id
                calendar_events.append({
                    'id': str(booking.id),
                    'title': f"{booking.room_name} - {'Your Booking' if is_user_booking else 'Booked'}",
                    'start': f"{booking.date}T{booking.start_time}",
                    'end': f"{booking.date}T{booking.end_time}",
                    'extendedProps': {
                        'isUserBooking': is_user_booking
                    }
                })
            
            data = {
                'all_bookings': calendar_events,
                'active_bookings': active_bookings,
                'upcoming_bookings': upcoming_bookings,
                'past_bookings': past_bookings
            }
            
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(5)  # Send updates every 5 seconds

    return Response(generate(), mimetype='text/event-stream')