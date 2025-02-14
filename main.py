from flask import Flask, render_template, request, redirect, session, jsonify, flash
import json
import os
import re

app = Flask(__name__)
app.secret_key = 'secretkeyyy'

# File paths
USER_FILE = 'users.json'
ROOM_FILE = 'rooms.json'

# Load JSON data
def load_data(file, default):
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump(default, f)
    with open(file, 'r') as f:
        return json.load(f)

def save_data(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

# Initialize files
users = load_data(USER_FILE, {})
rooms = load_data(ROOM_FILE, [
    {"id": 1, "type": "Single Room", "price": 50},
    {"id": 2, "type": "Double Room", "price": 80},
    {"id": 3, "type": "Suite", "price": 150}
])

# Email validation function
def is_valid_email(email):
    email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(email_regex, email)

# Routes
@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')
    user = session.get('user')
    return render_template('index.html', rooms=rooms, user=user)

@app.route('/cart')
def view_cart():
    if 'user' not in session:
        return redirect('/login')
    user = session.get('user')
    cart_items = users[user].get('cart', [])  # Assuming cart is stored in the user's data
    total_price = sum(item['price'] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total_price=total_price, user=user)

@app.route('/add_to_cart/<int:room_id>', methods=['POST'])
def add_to_cart(room_id):
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'})
    user = session.get('user')
    room = next((room for room in rooms if room['id'] == room_id), None)
    if room:
        if 'cart' not in users[user]:
            users[user]['cart'] = []
        users[user]['cart'].append(room)
        save_data(USER_FILE, users)
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Room not found'})

@app.route('/remove_from_cart/<int:room_id>', methods=['POST'])
def remove_from_cart(room_id):
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'})
    user = session.get('user')
    if 'cart' in users[user]:
        users[user]['cart'] = [item for item in users[user]['cart'] if item['id'] != room_id]
        save_data(USER_FILE, users)
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Cart not found'})

@app.route('/help')
def help_page():
    if 'user' not in session:
        return redirect('/login')
    user = session.get('user')
    return render_template('help.html', rooms=rooms, user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not is_valid_email(username):
            flash('Invalid email format!', 'danger')
            return render_template('register.html')
        if username in users:
            flash('User already exists!', 'danger')
            return render_template('register.html')
        users[username] = {'password': password}
        save_data(USER_FILE, users)
        flash('Registration successful! You can now log in.', 'success')
        return redirect('/')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not is_valid_email(username):
            flash('Invalid email format!', 'danger')
            return render_template('login.html')
        if username in users and users[username]['password'] == password:
            session['user'] = username
            flash('Login successful!', 'success')
            return redirect('/')
        flash('Invalid username or password!', 'danger')
        return render_template('login.html')  # Stay on the login page
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect('/login')

# Run the Flask app
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
