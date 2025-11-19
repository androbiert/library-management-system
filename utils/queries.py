from db import get_db
from bson.objectid import ObjectId
from datetime import datetime
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
        "created_at": datetime.utcnow()
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
        "available_copies": int(total_copies), # Initially same as total
        "added_at": datetime.utcnow()
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
    search_pattern = {"$regex": query, "$options": "i"}  # case-insensitive
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
    # If total_copies is updated, we might need to adjust available_copies logic, 
    # but for simplicity we'll just update fields passed in data.
    # In a real app, we'd check if total_copies < currently_borrowed.
    if 'total_copies' in data:
        data['total_copies'] = int(data['total_copies'])
        # We won't auto-update available_copies here to avoid inconsistencies without more logic
    
    db.books.update_one({"_id": ObjectId(book_id)}, {"$set": data})

def delete_book(book_id):
    db = get_db()
    db.books.delete_one({"_id": ObjectId(book_id)})

# --- Loan Operations ---

def create_loan(user_id, book_id, deadline):
    db = get_db()
    
    # 1. Check availability
    book = db.books.find_one({"_id": ObjectId(book_id)})
    if not book or book['available_copies'] < 1:
        return False, "Book not available"

    # 2. Create loan record
    loan = {
        "user_id": ObjectId(user_id),
        "book_id": ObjectId(book_id),
        "borrow_date": datetime.utcnow(),
        "deadline": deadline, # Expecting datetime object
        "return_date": None,
        "status": "Borrowed"
    }
    
    # 3. Transaction-like update (Atomic operations preferred)
    # Decrement available copies
    db.books.update_one({"_id": ObjectId(book_id)}, {"$inc": {"available_copies": -1}})
    
    result = db.loans.insert_one(loan)
    return True, result.inserted_id

def return_book(loan_id):
    db = get_db()
    loan = db.loans.find_one({"_id": ObjectId(loan_id)})
    if not loan or loan['status'] == "Returned":
        return False, "Invalid loan or already returned"

    # Update loan status
    db.loans.update_one(
        {"_id": ObjectId(loan_id)}, 
        {
            "$set": {
                "return_date": datetime.utcnow(),
                "status": "Returned"
            }
        }
    )
    
    # Increment available copies
    db.books.update_one({"_id": loan['book_id']}, {"$inc": {"available_copies": 1}})
    return True, "Book returned successfully"

def get_user_loans(user_id):
    db = get_db()
    # Join with books to get details
    pipeline = [
        {"$match": {"user_id": ObjectId(user_id)}},
        {"$lookup": {
            "from": "books",
            "localField": "book_id",
            "foreignField": "_id",
            "as": "book_details"
        }},
        {"$unwind": "$book_details"},
        {"$sort": {"borrow_date": -1}}
    ]
    return list(db.loans.aggregate(pipeline))

def get_all_loans():
    db = get_db()
    # Join with users and books
    pipeline = [
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "_id",
            "as": "user_details"
        }},
        {"$unwind": "$user_details"},
        {"$lookup": {
            "from": "books",
            "localField": "book_id",
            "foreignField": "_id",
            "as": "book_details"
        }},
        {"$unwind": "$book_details"},
        {"$sort": {"borrow_date": -1}}
    ]
    return list(db.loans.aggregate(pipeline))

def update_loan_status(loan_id, status):
    db = get_db()
    db.loans.update_one({"_id": ObjectId(loan_id)}, {"$set": {"status": status}})

def get_late_loans():
    """Get loans that are past deadline and not returned"""
    db = get_db()
    pipeline = [
        {"$match": {
            "status": {"$in": ["Borrowed", "Late"]},
            "deadline": {"$lt": datetime.utcnow()}
        }},
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "_id",
            "as": "user_details"
        }},
        {"$unwind": "$user_details"},
        {"$lookup": {
            "from": "books",
            "localField": "book_id",
            "foreignField": "_id",
            "as": "book_details"
        }},
        {"$unwind": "$book_details"}
    ]
    return list(db.loans.aggregate(pipeline))

def get_active_loans_count():
    """Count of loans that are not returned"""
    db = get_db()
    return db.loans.count_documents({"status": {"$in": ["Borrowed", "Late"]}})

def get_loans_by_category():
    """Get loan counts by book category for charts"""
    db = get_db()
    pipeline = [
        {"$lookup": {
            "from": "books",
            "localField": "book_id",
            "foreignField": "_id",
            "as": "book_details"
        }},
        {"$unwind": "$book_details"},
        {"$group": {
            "_id": "$book_details.category",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]
    return list(db.loans.aggregate(pipeline))

def get_loans_by_month():
    """Get loan counts by month for the current year"""
    db = get_db()
    pipeline = [
        {"$match": {
            "borrow_date": {
                "$gte": datetime(datetime.utcnow().year, 1, 1)
            }
        }},
        {"$group": {
            "_id": {"$month": "$borrow_date"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    return list(db.loans.aggregate(pipeline))

def get_loan_status_distribution():
    """Get distribution of loan statuses"""
    db = get_db()
    pipeline = [
        {"$group": {
            "_id": "$status",
            "count": {"$sum": 1}
        }}
    ]
    return list(db.loans.aggregate(pipeline))
