# app/routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import User

# Create a Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    return render_template('home.html')

@auth_bp.route('/about')
def about():
    return render_template('about.html')
    
# Route for user login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['username'] = username
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('notes.view_notes'))
        elif user is None:
            flash('Username does not exist. Please register first.', 'warning')
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('login.html')


# Route for user registration
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not password:
            flash('Username and password are required.', 'danger')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.register'))
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose another.', 'danger')
            return redirect(url_for('auth.register'))
        
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

# Route for user logout
@auth_bp.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('auth.login'))
    
    return render_template('dashboard.html')

@auth_bp.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    if 'username' not in session:
        flash('Please log in to delete your account.', 'warning')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        if user:
            db.session.delete(user)
            db.session.commit()
            session.pop('username', None)
            session.pop('user_id', None)
            flash('Your account has been deleted.', 'info')
        else:
            flash('User not found.', 'danger')
        
        return redirect(url_for('auth.login'))
    
    return render_template('delete_account.html')
