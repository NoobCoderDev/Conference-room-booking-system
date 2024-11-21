# Conference Room Booking System

## Overview

The Conference Room Booking System is a web-based application designed to streamline the process of reserving meeting spaces within an organization. This system allows users to view available rooms, book them for specific time slots, and manage their reservations efficiently.

## Features

- User authentication and authorization
- Real-time room availability display
- Room booking with date and time selection
- Recurring booking options
- Room details and capacity information
- Cancellation and modification of bookings
- Admin panel for room management
- Email notifications for bookings and reminders
- Integration with calendar applications (e.g., Google Calendar, Outlook)

## Technologies Used

- Backend: Python Flask
- Frontend: DashLite (HTML, CSS, JavaScript)
- Database: MongoDB
- ODM (Object Document Mapper): Flask-MongoEngine
- Authentication: Flask-Login
- Form Handling: Flask-WTF

## Installation

1. Clone the repository:
   git clone https://github.com/yourusername/conference-room-booking.git

2. Navigate to the project directory:
   cd conference-room-booking

3. Create a virtual environment and activate it:
   python -m venv env

4. Activate the Environment:
   cd env/Scripts/Activate

5. Install the required packages:
   pip install -r requirements.txt

6. Set up environment variables:
   Create a `.env` file in the root directory
   Add necessary variables (e.g., SECRET_KEY, MONGODB_URI, MAIL_SERVER)

7. Ensure MongoDB is installed and running on your system

8. Run the application:
   python app.py

## Usage

1. Open a web browser and go to `http://localhost:5000`
2. Register for an account or log in
3. Browse available rooms and time slots
4. Make a booking by selecting a room, date, and time
5. Manage your bookings through the user dashboard

## Contact

Devanshu Sonbhurra - [sonbhurra@gmail.com]
