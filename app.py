from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from config import Config
from db import init_app, get_db
from utils.queries import *
from werkzeug.security import check_password_hash
from functools import wraps
from datetime import datetime
import re

app = Flask(__name__)
app.config['APP_NAME'] = "Ktabna"
app.config.from_object(Config)

init_app(app)

# --- Decorators ---

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_user_by_id(user_id)

# --- Auth Routes ---

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = 'user'  # Always create new registrations as regular users (admins must be created by existing admins)
        
        if get_user_by_email(email):
            flash('Email already registered', 'error')
        else:
            create_user(username, email, password, role)
            flash('Registration successful. Please login.', 'success')
            return redirect(url_for('login'))
            
    return render_template('register.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username_or_email = request.form.get('username')  # Get username/email from form
        password = request.form['password']
        
        # Try to find user by username OR email
        user = None
        db = get_db()
        if username_or_email:
            # Check if it's an email (contains @) or username
            if '@' in username_or_email:
                user = db.users.find_one({'email': username_or_email})
            else:
                user = db.users.find_one({'username': username_or_email})
        
        if user and check_password_hash(user['password'], password):
            # Award badges on login
            award_badges(user['_id'])
            
            session.clear()
            session['user_id'] = str(user['_id'])
            session['role'] = user['role']
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_dashboard'))
        
        flash('Invalid username/email or password', 'error')
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- Main Routes ---

@app.route('/')
def index():
    # Redirect logged-in users to their dashboard
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    
    # Show public homepage only for guests
    books = get_all_books()
    categories = get_all_categories()
    users = get_all_users()
    
    # Get stats for homepage
    total_books = len(books)
    total_categories = len(categories)
    active_members = len([u for u in users if u['role'] == 'user'])
    
    return render_template('index.html', 
                         books=books, 
                         total_books=total_books,
                         total_categories=total_categories,
                         active_members=active_members)

# --- Admin Routes ---

@app.route('/admin')
@admin_required
def admin_dashboard():
    books = get_all_books()
    users = get_all_users()
    loans = get_all_loans()
    late_loans = get_late_loans()
    active_loans_count = get_active_loans_count()
    
    stats = {
        'total_books': len(books),
        'total_users': len(users),
        'total_loans': len(loans),
        'active_loans': active_loans_count,
        'late_returns': len(late_loans)
    }
    
    return render_template('admin/dashboard.html', books=books, users=users, loans=loans, 
                         late_loans=late_loans, stats=stats)

@app.route('/admin/books')
@admin_required
def manage_books():
    books = get_all_books()
    return render_template('admin/books.html', books=books)

@app.route('/admin/users')
@admin_required
def manage_users():
    users = get_all_users()
    return render_template('admin/users.html', users=users)

@app.route('/admin/loans')
@admin_required
def manage_loans():
    from datetime import datetime as dt
    books = get_all_books()
    users = get_all_users()
    loans = get_all_loans()
    late_loans = get_late_loans()
    return render_template('admin/loans.html', books=books, users=users, loans=loans, 
                         late_loans=late_loans, now=dt.utcnow)

@app.route('/api/stats')
@admin_required
def api_stats():
    """API endpoint for chart data"""
    from flask import jsonify
    
    loans_by_category = get_loans_by_category()
    loans_by_month = get_loans_by_month()
    loan_status_dist = get_loan_status_distribution()
    
    # Format data for Chart.js
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_data = [0] * 12
    for item in loans_by_month:
        monthly_data[item['_id'] - 1] = item['count']
    
    return jsonify({
        'category': {
            'labels': [item['_id'] for item in loans_by_category],
            'data': [item['count'] for item in loans_by_category]
        },
        'monthly': {
            'labels': month_names,
            'data': monthly_data
        },
        'status': {
            'labels': [item['_id'] for item in loan_status_dist],
            'data': [item['count'] for item in loan_status_dist]
        }
    })

@app.route('/admin/book/add', methods=('GET', 'POST'))
@admin_required
def add_book_route():
    if request.method == 'POST':
        title = request.form['title'].strip()
        author = request.form['author'].strip()
        db = get_db()
        existing_book = db.books.find_one({
            'title': {'$regex': f'^{re.escape(title)}$', '$options': 'i'},
            'author': {'$regex': f'^{re.escape(author)}$', '$options': 'i'}
        })
        if existing_book:
            flash('Book already exists', 'error')
            return redirect(url_for('add_book_route'))
        add_book(
            title,
            author,
            request.form['category'],
            request.form['description'],
            request.form['cover_image'],
            request.form['total_copies']
        )
        flash('Book added successfully', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/book_form.html', action="Add")

@app.route('/admin/book/edit/<book_id>', methods=('GET', 'POST'))
@admin_required
def edit_book_route(book_id):
    book = get_book_by_id(book_id)
    if request.method == 'POST':
        data = {
            "title": request.form['title'],
            "author": request.form['author'],
            "category": request.form['category'],
            "description": request.form['description'],
            "cover_image": request.form['cover_image'],
            "total_copies": int(request.form['total_copies'])
        }
        update_book(book_id, data)
        flash('Book updated successfully', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/book_form.html', book=book, action="Edit")

@app.route('/admin/book/delete/<book_id>')
@admin_required
def delete_book_route(book_id):
    delete_book(book_id)
    flash('Book deleted', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/user/add', methods=('GET', 'POST'))
@admin_required
def add_user_route():
    if request.method == 'POST':
        create_user(
            request.form['username'],
            request.form['email'],
            request.form['password'],
            request.form['role']
        )
        flash('User added', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/user_form.html')

@app.route('/admin/loan/assign', methods=('POST',))
@admin_required
def assign_loan_route():
    user_id = request.form['user_id']
    book_id = request.form['book_id']
    deadline_str = request.form['deadline']
    deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
    
    success, msg = create_loan(user_id, book_id, deadline)
    if success:
        flash('Book assigned successfully', 'success')
    else:
        flash(f'Error: {msg}', 'error')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/loan/return/<loan_id>')
@admin_required
def return_loan_route(loan_id):
    success, msg = return_book(loan_id)
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'error')
    return redirect(url_for('admin_dashboard'))

# --- User Routes ---

@app.route('/dashboard')
@login_required
def user_dashboard():
    category = request.args.get('category')
    search_query = request.args.get('search')
    
    if search_query:
        books = search_books(search_query)
    elif category:
        books = get_all_books({'category': category})
    else:
        books = get_all_books()
    
    categories = get_all_categories()
    badge_count = len(get_user_badges(session['user_id']))
    
    return render_template('user/dashboard.html', books=books, categories=categories, 
                         current_category=category, search_query=search_query, badge_count=badge_count)

@app.route('/borrow/<book_id>', methods=('POST',))
@login_required
def borrow_book_route(book_id):
    from datetime import timedelta
    
    # Check if user already has an active borrowed book (using new embedded approach)
    if check_user_has_active_loan(session['user_id']):
        flash('You already have an active book. Please return it before borrowing another one.', 'error')
        return redirect(url_for('user_dashboard'))
    
    # Set deadline to 14 days from now
    deadline = datetime.utcnow() + timedelta(days=14)
    
    success, msg = create_loan(session['user_id'], book_id, deadline)
    if success:
        # Increment books_read and award badges
        db = get_db()
        db.users.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$inc': {'books_read': 1}}
        )
        award_badges(session['user_id'])
        
        flash('Book borrowed successfully! Please return within 14 days.', 'success')
    else:
        flash(f'Error: {msg}', 'error')
    return redirect(url_for('user_dashboard'))

@app.route('/my_loans')
@login_required
def my_loans():
    loans = get_user_loans(session['user_id'])
    return render_template('user/my_loans.html', loans=loans)

@app.route('/badges')
@login_required
def user_badges():
    """Display user's earned and locked badges"""
    from utils.queries import BADGE_DEFINITIONS, get_user_badges
    
    # Get user's earned badges
    earned_badges = get_user_badges(session['user_id'])
    earned_badge_ids = {badge['id'] for badge in earned_badges}
    
    # Get locked badges (all badges not earned)
    locked_badges = []
    for badge_id, badge_info in BADGE_DEFINITIONS.items():
        if badge_id not in earned_badge_ids:
            locked_badges.append({
                'id': badge_id,
                'name': badge_info['name'],
                'description': badge_info['description']
            })
    
    return render_template('user/badges.html', 
                         badges=earned_badges,
                         locked_badges=locked_badges,
                         total_badges=len(BADGE_DEFINITIONS))


@app.route('/return/<loan_id>', methods=('POST',))
@login_required
def user_return_book(loan_id):
    # Verify that this loan belongs to the current user (using embedded approach)
    from bson.objectid import ObjectId
    user = get_user_by_id(session['user_id'])
    
    # Find the loan in user's loans array
    loan = None
    for l in user.get('loans', []):
        if l['loan_id'] == ObjectId(loan_id):
            loan = l
            break
    
    if not loan:
        flash('Loan not found or you do not have permission to return this book', 'error')
        return redirect(url_for('my_loans'))
    
    success, msg = return_book(loan_id)
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'error')
    return redirect(url_for('my_loans'))

# --- Book Detail Routes (AI-Powered) ---

@app.route('/book/<book_id>')
def book_detail(book_id):
    """Display detailed book information with AI-generated recommendations"""
    book = get_book_by_id(book_id)
    if not book:
        flash('Book not found', 'error')
        return redirect(url_for('index'))
    
    return render_template('book_detail.html', book=book)

@app.route('/api/book/<book_id>/ai-recommendation')
def get_ai_recommendation(book_id):
    """API endpoint to get AI-generated book recommendation"""
    from flask import jsonify
    from utils.ai_service import get_or_generate_recommendation
    
    book = get_book_by_id(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    # Generate or retrieve cached recommendation
    recommendation = get_or_generate_recommendation(book)
    
    return jsonify(recommendation)

if __name__ == '__main__':
    app.run(debug=True)
