from db import get_db
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

# --- User Operations ---

def create_user(username, email, password, role='user'):
    db = get_db()
    hashed_password = generate_password_hash(password)
    user = {
        "username": username,
        "email": email,
        "password": hashed_password,
        "role": role,
        "created_at": datetime.utcnow(),
        "loans": []  # Initialize empty loans array
    }
    result = db.users.insert_one(user)
    return result.inserted_id

def get_user_by_email(email):
    db = get_db()
    return db.users.find_one({"email": email})

def get_user_by_id(user_id):
    db = get_db()
    return db.users.find_one({"_id": ObjectId(user_id)})

def get_all_users():
    db = get_db()
    return list(db.users.find())

def update_user(user_id, data):
    db = get_db()
    db.users.update_one({"_id": ObjectId(user_id)}, {"$set": data})

def delete_user(user_id):
    db = get_db()
    db.users.delete_one({"_id": ObjectId(user_id)})

# --- Book Operations ---

def add_book(title, author, category, description, cover_image, total_copies):
    db = get_db()
    book = {
        "title": title,
        "author": author,
        "category": category,
        "description": description,
        "cover_image": cover_image,
        "total_copies": int(total_copies),
        "available_copies": int(total_copies),
        "added_at": datetime.utcnow(),
        "current_loans": [],  # Initialize empty current loans array
        "loan_history": []    # Initialize empty loan history array
    }
    result = db.books.insert_one(book)
    return result.inserted_id

def get_all_books(filter_query=None):
    db = get_db()
    query = filter_query if filter_query else {}
    return list(db.books.find(query))

def get_all_categories():
    db = get_db()
    return db.books.distinct("category")

def search_books(query):
    """Search books by title, author, or category using regex"""
    db = get_db()
    search_pattern = {"$regex": query, "$options": "i"}
    search_query = {
        "$or": [
            {"title": search_pattern},
            {"author": search_pattern},
            {"category": search_pattern}
        ]
    }
    return list(db.books.find(search_query))

def get_book_by_id(book_id):
    db = get_db()
    return db.books.find_one({"_id": ObjectId(book_id)})

def update_book(book_id, data):
    db = get_db()
    if 'total_copies' in data:
        data['total_copies'] = int(data['total_copies'])
    db.books.update_one({"_id": ObjectId(book_id)}, {"$set": data})

def delete_book(book_id):
    db = get_db()
    db.books.delete_one({"_id": ObjectId(book_id)})

# --- Loan Operations (Embedded Arrays) ---

def create_loan(user_id, book_id, deadline):
    """
    Create a loan by adding it to user's loans array and book's current_loans array
    """
    db = get_db()
    
    # 1. Check availability
    book = db.books.find_one({"_id": ObjectId(book_id)})
    if not book or book['available_copies'] < 1:
        return False, "Book not available"
    
    # 2. Get user info
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return False, "User not found"
    
    # 3. Generate loan ID
    loan_id = ObjectId()
    
    # 4. Add loan to user's loans array
    db.users.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$push": {
                "loans": {
                    "loan_id": loan_id,
                    "book_id": ObjectId(book_id),
                    "book_snapshot": {
                        "title": book['title'],
                        "author": book['author'],
                        "category": book['category'],  # FIXED: Added category for pie chart
                        "cover_image": book['cover_image']
                    },
                    "borrow_date": datetime.utcnow(),
                    "deadline": deadline,
                    "return_date": None,
                    "status": "Borrowed"
                }
            }
        }
    )
    
    # 5. Add loan to book's current_loans array and decrement available_copies
    db.books.update_one(
        {"_id": ObjectId(book_id)},
        {
            "$push": {
                "current_loans": {
                    "loan_id": loan_id,
                    "user_id": ObjectId(user_id),
                    "user_name": user['username'],
                    "borrow_date": datetime.utcnow(),
                    "deadline": deadline,
                    "status": "Borrowed"
                }
            },
            "$inc": {"available_copies": -1}
        }
    )
    
    return True, loan_id

def return_book(loan_id):
    """
    Return a book by updating the loan status in user's loans array  
    and moving it from current_loans to loan_history in book document
    """
    db = get_db()
    
    # 1. Find user with this loan
    user = db.users.find_one({"loans.loan_id": ObjectId(loan_id)})
    if not user:
        return False, "Loan not found"
    
    # Find the specific loan
    loan = None
    for l in user['loans']:
        if l['loan_id'] == ObjectId(loan_id):
            loan = l
            break
    
    if not loan or loan['status'] == "Returned":
        return False, "Invalid loan or already returned"
    
    # 2. Update loan status in user's loans array using positional operator
    db.users.update_one(
        {
            "_id": user['_id'],
            "loans.loan_id": ObjectId(loan_id)
        },
        {
            "$set": {
                "loans.$.return_date": datetime.utcnow(),
                "loans.$.status": "Returned"
            }
        }
    )
    
    # 3. Find the loan in book's current_loans
    book = db.books.find_one({
        "_id": loan['book_id'],
        "current_loans.loan_id": ObjectId(loan_id)
    })
    
    if book:
        # Find the specific current loan
        current_loan = None
        for cl in book['current_loans']:
            if cl['loan_id'] == ObjectId(loan_id):
                current_loan = cl
                break
        
        if current_loan:
            # 4. Remove from current_loans, add to loan_history, increment available_copies
            db.books.update_one(
                {"_id": loan['book_id']},
                {
                    "$pull": {"current_loans": {"loan_id": ObjectId(loan_id)}},
                    "$push": {
                        "loan_history": {
                            "loan_id": current_loan['loan_id'],
                            "user_id": current_loan['user_id'],
                            "user_name": current_loan['user_name'],
                            "borrow_date": current_loan['borrow_date'],
                            "return_date": datetime.utcnow(),
                            "status": "Returned"
                        }
                    },
                    "$inc": {"available_copies": 1}
                }
            )
    
    return True, "Book returned successfully"

def get_user_loans(user_id):
    """
    Get user's loans directly from their embedded loans array
    No aggregation needed - book info is already in book_snapshot!
    """
    db = get_db()
    user = db.users.find_one({"_id": ObjectId(user_id)})
    
    if not user or 'loans' not in user:
        return []
    
    # Return loans sorted by borrow_date (most recent first)
    loans = user['loans']
    loans_sorted = sorted(loans, key=lambda x: x['borrow_date'], reverse=True)
    
    # Convert to list format similar to old aggregation output for compatibility
    result = []
    for loan in loans_sorted:
        result.append({
            "_id": loan['loan_id'],
            "loan_id": loan['loan_id'],
            "book_id": loan['book_id'],
            "borrow_date": loan['borrow_date'],
            "deadline": loan['deadline'],
            "return_date": loan.get('return_date'),
            "status": loan['status'],
            "book_details": loan['book_snapshot']  # Book info already embedded!
        })
    
    return result

def get_all_loans():
    """
    Get all loans from all users with aggregation
    """
    db = get_db()
    pipeline = [
        {"$unwind": "$loans"},
        {
            "$project": {
                "user_details": {
                    "username": "$username",
                    "email": "$email",
                    "_id": "$_id"
                },
                "loan_id": "$loans.loan_id",
                "book_id": "$loans.book_id",
                "book_details": "$loans.book_snapshot",
                "borrow_date": "$loans.borrow_date",
                "deadline": "$loans.deadline",
                "return_date": "$loans.return_date",
                "status": "$loans.status"
            }
        },
        {"$sort": {"borrow_date": -1}}
    ]
    return list(db.users.aggregate(pipeline))

def update_loan_status(loan_id, status):
    """Update loan status in user's loans array"""
    db = get_db()
    db.users.update_one(
        {"loans.loan_id": ObjectId(loan_id)},
        {"$set": {"loans.$.status": status}}
    )

def get_late_loans():
    """Get loans that are past deadline and not returned"""
    db = get_db()
    pipeline = [
        {"$unwind": "$loans"},
        {
            "$match": {
                "loans.status": {"$in": ["Borrowed", "Late"]},
                "loans.deadline": {"$lt": datetime.utcnow()}
            }
        },
        {
            "$project": {
                "user_details": {
                    "username": "$username",
                    "email": "$email",
                    "_id": "$_id"
                },
                "loan_id": "$loans.loan_id",
                "book_id": "$loans.book_id",
                "book_details": "$loans.book_snapshot",
                "borrow_date": "$loans.borrow_date",
                "deadline": "$loans.deadline",
                "return_date": "$loans.return_date",
                "status": "$loans.status"
            }
        }
    ]
    return list(db.users.aggregate(pipeline))

def get_active_loans_count():
    """Count of loans that are not returned"""
    db = get_db()
    pipeline = [
        {"$unwind": "$loans"},
        {
            "$match": {
                "loans.status": {"$in": ["Borrowed", "Late"]}
            }
        },
        {"$count": "active_loans"}
    ]
    result = list(db.users.aggregate(pipeline))
    return result[0]['active_loans'] if result else 0

def get_loans_by_category():
    """Get loan counts by book category for charts"""
    db = get_db()
    pipeline = [
        {"$unwind": "$loans"},
        {
            "$group": {
                "_id": "$loans.book_snapshot.category",
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"count": -1}}
    ]
    # Filter out None categories
    results = list(db.users.aggregate(pipeline))
    return [r for r in results if r['_id'] is not None]

def get_loans_by_month():
    """Get loan counts by month for the current year"""
    db = get_db()
    pipeline = [
        {"$unwind": "$loans"},
        {
            "$match": {
                "loans.borrow_date": {
                    "$gte": datetime(datetime.utcnow().year, 1, 1)
                }
            }
        },
        {
            "$group": {
                "_id": {"$month": "$loans.borrow_date"},
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    return list(db.users.aggregate(pipeline))

def get_loan_status_distribution():
    """Get distribution of loan statuses"""
    db = get_db()
    pipeline = [
        {"$unwind": "$loans"},
        {
            "$group": {
                "_id": "$loans.status",
                "count": {"$sum": 1}
            }
        }
    ]
    return list(db.users.aggregate(pipeline))

def check_user_has_active_loan(user_id):
    """Check if user has any active loans (Borrowed or Late status)"""
    db = get_db()
    user = db.users.find_one({
        "_id": ObjectId(user_id),
        "loans": {
            "$elemMatch": {
                "status": {"$in": ["Borrowed", "Late"]}
            }
        }
    })
    return user is not None

# --- Badge System ---

BADGE_DEFINITIONS = {
    "welcome": {
        "name": "Welcome",
        "description": "First login to the platform.",
        "criteria": lambda user: True,  # Awarded on first login
    },
    "first_reader": {
        "name": "First Reader",
        "description": "Read your first book.",
        "criteria": lambda user: user.get('books_read', 0) >= 1,
    },
    "bookworm": {
        "name": "Bookworm",
        "description": "Read 5 books.",
        "criteria": lambda user: user.get('books_read', 0) >= 5,
    },
    "scholar": {
        "name": "Scholar",
        "description": "Read 20 books.",
        "criteria": lambda user: user.get('books_read', 0) >= 20,
    },
    "master_reader": {
        "name": "Master Reader",
        "description": "Read 50 books.",
        "criteria": lambda user: user.get('books_read', 0) >= 50,
    },
    "legendary_reader": {
        "name": "Legendary Reader",
        "description": "Read 100 books.",
        "criteria": lambda user: user.get('books_read', 0) >= 100,
    },
    "explorer": {
        "name": "Explorer",
        "description": "Browse more than 10 different categories.",
        "criteria": lambda user: len(user.get('categories_explored', [])) >= 10,
    },
}

def award_badges(user_id):
    """Check user data and award any new badges."""
    db = get_db()
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return []
    
    # Initialize badge fields if they don't exist
    if 'badges' not in user:
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"badges": [], "books_read": 0, "categories_explored": []}}
        )
        user['badges'] = []
        user['books_read'] = 0
        user['categories_explored'] = []
    
    earned = []
    existing_badge_ids = {b.get("badge_id") for b in user.get('badges', [])}
    
    for badge_key, badge_info in BADGE_DEFINITIONS.items():
        if badge_key in existing_badge_ids:
            continue
        try:
            if badge_info["criteria"](user):
                # Add badge entry
                badge_entry = {
                    "badge_id": badge_key,
                    "earned_at": datetime.utcnow(),
                }
                db.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$push": {"badges": badge_entry}}
                )
                earned.append(badge_key)
        except Exception as e:
            # In case criteria lambda raises error, ignore badge
            continue
    
    return earned

def get_user_badges(user_id):
    """Get all badges earned by a user with their details."""
    db = get_db()
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return []
    
    badges = []
    for badge_entry in user.get('badges', []):
        badge_key = badge_entry.get('badge_id')
        badge_def = BADGE_DEFINITIONS.get(badge_key, {})
        badges.append({
            "id": badge_key,
            "name": badge_def.get('name', badge_key),
            "description": badge_def.get('description', ''),
            "earned_at": badge_entry.get('earned_at')
        })
    return badges
