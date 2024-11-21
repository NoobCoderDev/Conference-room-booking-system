from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash
from models import User, Admin
from pymongo.errors import DuplicateKeyError

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.get_by_email(email)
        if user and user.check_password(password):
            login_user(user)
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        checkbox = request.form.get('checkbox')

        # Validate input
        if not name or not email or not password:
            return jsonify({'success': False, 'message': 'All fields are required'}), 400

        if not checkbox:
            return jsonify({'success': False, 'message': 'You must agree to the terms and conditions'}), 400

        # Check if user already exists
        existing_user_name = User.get_by_name(name)
        if existing_user_name:
            return jsonify({'success': False, 'message': 'Username already exists'}), 400

        # Check if user already exists
        existing_user_email = User.get_by_email(email)
        if existing_user_email:
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
        
        # Create new user
        try:
            new_user = User(
                name=name,
                email=email,
                password_hash=generate_password_hash(password)
            )
            result = new_user.save()
            if result.inserted_id:
                # Log the user in
                new_user.id = str(result.inserted_id)
                login_user(new_user)
                return jsonify({'success': True, 'message': 'Registration successful'}), 200
            else:
                return jsonify({'success': False, 'message': 'Failed to create user'}), 500

        except DuplicateKeyError:
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
        except Exception as e:
            return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'}), 500

    # GET request - render the registration form
    return render_template('auth/registor.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/*')
@auth.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404