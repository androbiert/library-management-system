from app import app
from utils.queries import create_user, add_book, get_all_books, get_user_by_email
from db import get_db

def test_db_operations():
    with app.app_context():
        db = get_db()
        print("Connected to database:", db.name)
        
        # Test User Creation
        email = "admin@library.com"
        if not get_user_by_email(email):
            create_user("admin", email, "password123", "admin")
            print("Admin created.")
        else:
            print("Admin already exists.")
            
        # Test Book Addition
        books = get_all_books()
        if not books:
            add_book("The Great Gatsby", "F. Scott Fitzgerald", "Classic", "A novel about the American Dream.", "", 10)
            print("Book added.")
        else:
            print(f"Books found: {len(books)}")

if __name__ == "__main__":
    test_db_operations()
