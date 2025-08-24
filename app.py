from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import os
from datetime import datetime
from calculations import calculate_loan_payment, calculate_annual_dream_cost

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_change_in_production')

# MongoDB connection
# Replace with your actual MongoDB Atlas connection string
MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/lifepath_db?retryWrites=true&w=majority')

# Simple in-memory storage for development/testing
DEV_MODE = os.environ.get('DEV_MODE', 'true').lower() == 'true'

if DEV_MODE:
    print("WARNING: Running in development mode with in-memory storage")
    users_collection = None
    # Simple in-memory user storage for development
    dev_users = {}
    dev_user_counter = 1
else:
    try:
        client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
        client.admin.command('ping')
        print("SUCCESS: Connected to MongoDB!")
        db = client.lifepath_db
        users_collection = db.users
        dev_users = None
    except Exception as e:
        print(f"ERROR: MongoDB connection failed: {e}")
        print("WARNING: Falling back to development mode")
        users_collection = None
        dev_users = {}
        dev_user_counter = 1

# Development mode helper functions
def get_user_by_username(username):
    if users_collection:
        return users_collection.find_one({'username': username})
    else:
        for user_id, user_data in dev_users.items():
            if user_data['username'] == username:
                return {'_id': user_id, **user_data}
        return None

def get_user_by_id(user_id):
    if users_collection:
        return users_collection.find_one({'_id': ObjectId(user_id)})
    else:
        return dev_users.get(user_id)

def create_user(user_doc):
    global dev_user_counter
    if users_collection:
        result = users_collection.insert_one(user_doc)
        return str(result.inserted_id)
    else:
        user_id = str(dev_user_counter)
        dev_users[user_id] = user_doc
        dev_user_counter += 1
        return user_id

def update_user(user_id, update_data):
    if users_collection:
        users_collection.update_one(
            {'_id': ObjectId(user_id)},
            update_data
        )
    else:
        if user_id in dev_users:
            for key, value in update_data.get('$set', {}).items():
                keys = key.split('.')
                current = dev_users[user_id]
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                current[keys[-1]] = value
            
            for key, value in update_data.get('$push', {}).items():
                keys = key.split('.')
                current = dev_users[user_id]
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                if keys[-1] not in current:
                    current[keys[-1]] = []
                current[keys[-1]].append(value)

# Routes
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if user already exists
        if get_user_by_username(username):
            flash('Username already exists')
            return render_template('register.html')
        
        # Create new user
        password_hash = generate_password_hash(password)
        user_doc = {
            'username': username,
            'password_hash': password_hash,
            'created_at': datetime.utcnow(),
            'profile': {
                'dream': {},
                'reality': {},
                'path': {}
            }
        }
        
        user_id = create_user(user_doc)
        session['user_id'] = user_id
        session['username'] = username
        
        flash('Registration successful!')
        return redirect(url_for('onboarding_dream'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = get_user_by_username(username)
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = str(user['_id'])
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/onboarding/dream', methods=['GET', 'POST'])
def onboarding_dream():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        dream_data = {
            'target_city': request.form['target_city'],
            'housing_cost': float(request.form['housing_cost']),
            'transportation_cost': float(request.form['transportation_cost']),
            'food_cost': float(request.form.get('food_cost', 0)),
            'entertainment_cost': float(request.form.get('entertainment_cost', 0)),
            'other_cost': float(request.form.get('other_cost', 0))
        }
        
        # Calculate annual dream cost
        dream_data['annual_dream_cost'] = calculate_annual_dream_cost(dream_data)
        
        # Update user profile
        update_user(session['user_id'], {'$set': {'profile.dream': dream_data}})
        
        return redirect(url_for('onboarding_reality'))
    
    return render_template('onboarding/dream.html')

@app.route('/onboarding/reality', methods=['GET', 'POST'])
def onboarding_reality():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        reality_data = {
            'monthly_income': float(request.form['monthly_income']),
            'expenses': []
        }
        
        # Process expenses
        expense_categories = request.form.getlist('expense_category')
        expense_amounts = request.form.getlist('expense_amount')
        
        for category, amount in zip(expense_categories, expense_amounts):
            if category and amount:
                reality_data['expenses'].append({
                    'category': category,
                    'amount': float(amount)
                })
        
        # Update user profile
        update_user(session['user_id'], {'$set': {'profile.reality': reality_data}})
        
        return redirect(url_for('onboarding_path'))
    
    return render_template('onboarding/reality.html')

@app.route('/onboarding/path', methods=['GET', 'POST'])
def onboarding_path():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        path_data = {
            'plan': request.form['plan']
        }
        
        if path_data['plan'] == 'college':
            annual_tuition = float(request.form['annual_tuition'])
            financial_aid = float(request.form.get('financial_aid', 0))
            years = int(request.form.get('years', 4))
            
            total_debt = (annual_tuition - financial_aid) * years
            monthly_payment = calculate_loan_payment(total_debt) if total_debt > 0 else 0
            
            path_data.update({
                'college_name': request.form['college_name'],
                'annual_tuition': annual_tuition,
                'financial_aid': financial_aid,
                'years': years,
                'total_debt': total_debt,
                'estimated_loan_payment': monthly_payment,
                'projected_starting_salary': float(request.form['projected_starting_salary'])
            })
        
        elif path_data['plan'] == 'workforce':
            path_data['projected_starting_salary'] = float(request.form['projected_starting_salary'])
        
        # Update user profile
        update_user(session['user_id'], {'$set': {'profile.path': path_data}})
        
        return redirect(url_for('dashboard'))
    
    return render_template('onboarding/path.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    if not user.get('profile') or not all(user['profile'].get(section) for section in ['dream', 'reality', 'path']):
        return redirect(url_for('onboarding_dream'))
    
    return render_template('dashboard.html', user_data=user)

@app.route('/tools/subscriptions')
def subscription_audit():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    return render_template('tools/subscriptions.html', user_data=user)

@app.route('/api/expense', methods=['POST'])
def add_expense():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    category = request.json.get('category')
    amount = float(request.json.get('amount'))
    
    update_user(session['user_id'], {'$push': {'profile.reality.expenses': {'category': category, 'amount': amount}}})
    
    return jsonify({'success': True})

@app.route('/api/expense/<int:index>', methods=['DELETE'])
def remove_expense(index):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = get_user_by_id(session['user_id'])
    if not user or 'profile' not in user or 'reality' not in user['profile']:
        return jsonify({'error': 'User data not found'}), 404
    
    expenses = user['profile']['reality']['expenses']
    
    if 0 <= index < len(expenses):
        expenses.pop(index)
        update_user(session['user_id'], {'$set': {'profile.reality.expenses': expenses}})
    
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
