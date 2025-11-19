"""
Database Seeding Script
Run this script to populate the database with predefined users and books.
This ensures your team has initial data to work with.

Usage: python seed_db.py
"""

from app import app
from db import get_db
from utils.queries import (
    create_user, get_user_by_email,
    add_book, get_all_books
)

def seed_database():
    """Seed the database with predefined users and books."""
    with app.app_context():
        db = get_db()
        print("=" * 60)
        print("DATABASE SEEDING SCRIPT")
        print("=" * 60)
        print(f"Connected to database: {db.name}\n")
        
        # Predefined Users
        users = [
            {
                "name": "admin",
                "email": "admin@library.com",
                "password": "admin123",
                "role": "admin"
            },
            {
                "name": "Andro",
                "email": "andro@library.com",
                "password": "andro123",
                "role": "user"
            },
            {
                "name": "Ali",
                "email": "ali@library.com",
                "password": "ali123",
                "role": "user"
            },
            {
                "name": "Farah",
                "email": "farah@library.com",
                "password": "farah123",
                "role": "user"
            },
            {
                "name": "Feriel",
                "email": "feriel@library.com",
                "password": "feriel123",
                "role": "user"
            }
        ]
        
 
        books = [
            {
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "genre": "Classic",
                "description": "A novel about the American Dream set in the Jazz Age.",
                "image_url": "https://tse4.mm.bing.net/th/id/OIP.LpBw0Rr0-CJI8yLsQeCoBAHaLW?rs=1&pid=ImgDetMain&o=7&rm=3",
                "stock": 5
            },
            {
                "title": "To Kill a Mockingbird",
                "author": "Harper Lee",
                "genre": "Classic",
                "description": "A gripping tale of racial injustice and childhood innocence in the American South.",
                "image_url": "https://tse3.mm.bing.net/th/id/OIP.nrnuq3_OK0li1FoN9OrGgwHaLG?rs=1&pid=ImgDetMain&o=7&rm=3",
                "stock": 4
            },
            {
                "title": "1984",
                "author": "George Orwell",
                "genre": "Science Fiction",
                "description": "A dystopian novel about totalitarianism and surveillance.",
                "image_url": "https://th.bing.com/th/id/R.13d7f73f69fe932fc40b56b9289c6288?rik=4UFEgWx3coLB5w&pid=ImgRaw&r=0",
                "stock": 6
            },
            {
                "title": "Pride and Prejudice",
                "author": "Jane Austen",
                "genre": "Romance",
                "description": "A romantic novel of manners set in Georgian England.",
                "image_url": "https://static1.srcdn.com/wordpress/wp-content/uploads/2024/05/pride-and-prejudice-1995.jpg",
                "stock": 3
            },
            {
                "title": "The Hobbit",
                "author": "J.R.R. Tolkien",
                "genre": "Fantasy",
                "description": "A fantasy adventure following Bilbo Baggins on an unexpected journey.",
                "image_url": "https://tse2.mm.bing.net/th/id/OIP.To2r-UghMb79tPasgHo37wHaLH?rs=1&pid=ImgDetMain&o=7&rm=3",
                "stock": 7
            },
            {
                "title": "Harry Potter and the Sorcerer's Stone",
                "author": "J.K. Rowling",
                "genre": "Fantasy",
                "description": "The first book in the magical Harry Potter series.",
                "image_url": "https://m.media-amazon.com/images/S/pv-target-images/ba065eabc6306d12da6fe914549d6ab6464c9e3c0cee323a1c953595bec1a5cf.jpg",
                "stock": 8
            },
            {
                "title": "The Catcher in the Rye",
                "author": "J.D. Salinger",
                "genre": "Classic",
                "description": "A story about teenage rebellion and alienation.",
                "image_url": "https://bibliomaniapublishing.com/wp-content/uploads/2024/03/The-Catcher-in-the-Rye-716x1024.png",
                "stock": 4
            },
            {
                "title": "Brave New World",
                "author": "Aldous Huxley",
                "genre": "Science Fiction",  
                "description": "A dystopian novel exploring a futuristic World State.",
                "image_url": "https://tse4.mm.bing.net/th/id/OIP.iSzuQdvhX7D9nJ1y8ICzTgHaKd?w=670&h=946&rs=1&pid=ImgDetMain&o=7&rm=3",
                "stock": 5
            },
            {
                "title": "The Lord of the Rings",
                "author": "J.R.R. Tolkien",
                "genre": "Fantasy",
                "description": "An epic fantasy trilogy about the quest to destroy the One Ring.",
                "image_url": "https://tse2.mm.bing.net/th/id/OIP.xLsF-29v0bUucu4gmF286QHaLH?rs=1&pid=ImgDetMain&o=7&rm=3",
                "stock": 6
            },
            {
                "title": "Moby-Dick",
                "author": "Herman Melville",
                "genre": "Classic",
                "description": "The narrative of Captain Ahab's obsessive quest for the white whale.",
                "image_url": "https://th.bing.com/th/id/R.dbf94ee4f77538f188af2d228769e1eb?rik=AqOCRfOQ%2bbCWEg&riu=http%3a%2f%2fstatic1.businessinsider.com%2fimage%2f5578a5e4eab8eab83fc1680c-1200%2fmoby-dick-by-herman-melville.jpg&ehk=gX%2fSlTuzz5s8AKdb%2bEJXP55y8Qby9f%2bATNNJi87ukNE%3d&risl=&pid=ImgRaw&r=0",
                "stock": 3
            },

            {
                "title": "The Alchemist",
                "author": "Paulo Coelho",
                "genre": "Fiction",
                "description": "A philosophical novel about following your dreams.",
                "image_url": "https://tse2.mm.bing.net/th/id/OIP.TYtiazLfVQ36w5tsCT43RwHaLO?rs=1&pid=ImgDetMain&o=7&rm=3",
                "stock": 7
            }
        ]
        

        print("SEEDING USERS")
        print("-" * 60)
        users_created = 0
        users_existing = 0
        
        for user in users:
            if not get_user_by_email(user["email"]):
                create_user(
                    user["name"],
                    user["email"],
                    user["password"],
                    user["role"]
                )
                users_created += 1
                role_badge = "[ADMIN]" if user["role"] == "admin" else "[USER]"
                print(f"✓ Created {role_badge}: {user['name']} ({user['email']})")
            else:
                users_existing += 1
                print(f"• Already exists: {user['name']} ({user['email']})")
        
        print(f"\nUsers Summary: {users_created} created, {users_existing} already existed")
        
        # Seed Books
        print(f"\n{'=' * 60}")
        print("SEEDING BOOKS")
        print("-" * 60)
        
        existing_books = get_all_books()
        
        if len(existing_books) > 0:
            books_created = 0
            for book in books:
                add_book(
                    book["title"],
                    book["author"],
                    book["genre"],
                    book["description"],
                    book["image_url"],
                    book["stock"]
                )
                books_created += 1
                print(f"✓ Added: {book['title']} by {book['author']} (Stock: {book['stock']})")
            
            print(f"\nBooks Summary: {books_created} books added")
        else:
            print(f"• Books already exist in database: {len(existing_books)} books found")
            print("• Skipping book seeding to avoid duplicates")
        
        # Final Summary
        print(f"\n{'=' * 60}")
        print("SEEDING COMPLETE!")
        print("=" * 60)
        print("\nYou can now login with:")
        print("  ADMIN: admin@library.com / admin123")
        print("  USER:  andro@library.com / andro123")
        print(f"\nTotal Users in DB: {len(users)}")
        print(f"Total Books in DB: {len(get_all_books())}")
        print("=" * 60)

if __name__ == "__main__":
    seed_database()
