# Ktabna - Library Management System 📚

A complete Library Management System built with Flask and MongoDB (NoSQL database).

## Features ✨
- **Admin Dashboard**: Manage books, users, and loans
- **User Interface**: Browse books, borrow/return, view loan history
- **NoSQL Database**: MongoDB with optimized schema design
- **Modern UI**: Clean and responsive design with blur effects

## Prerequisites 🔧
- Python 3.x
- MongoDB installed and running locally on port 27017

## Quick Start 🚀

### 1. Clone the Repository
```bash
git clone https://github.com/androbiert/library-management-system.git
cd library_system
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

### 4. Seed the Database
Run the seeding script to populate the database with predefined users and books:
```bash
python seed_db.py
```

This will create:
- **1 Admin user** and **4 Regular users**
- **12 Books** across various genres (Classic, Fantasy, Science Fiction, etc.)

### 5. Run the Application
```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000`

## 🔐 Predefined Login Credentials

After running `seed_db.py`, you can login with:

### Admin Account
- **Email**: `admin@library.com`
- **Password**: `admin123`

### User Accounts
- **Email**: `andro@library.com` | **Password**: `andro123`
- **Email**: `ali@library.com` | **Password**: `ali123`
- **Email**: `farah@library.com` | **Password**: `farah123`
- **Email**: `feriel@library.com` | **Password**: `feriel123`

## 📁 Project Structure
```
library_system/
├── app.py              # Main Flask application
├── db.py               # Database connection
├── config.py           # Configuration settings
├── seed_db.py          # Database seeding script
├── utils/
│   └── queries.py      # NoSQL query functions
├── templates/          # HTML templates
├── static/
│   ├── css/           # Stylesheets
│   └── js/            # JavaScript files
└── QUERIES.md         # NoSQL queries documentation
```

## 📖 Documentation
- **NoSQL Queries**: See `QUERIES.md` for detailed MongoDB query examples
- **Query Implementation**: Check `utils/queries.py` for Python implementation

## 🤝 For Team Members

When you clone this repository:
1. Make sure MongoDB is running on your machine
2. Install dependencies: `pip install -r requirements.txt`
3. Run the seeding script: `python seed_db.py`
4. Start the application: `python app.py`
5. Login using any of the predefined accounts above

## 🛠️ Technology Stack
- **Backend**: Flask (Python)
- **Database**: MongoDB (NoSQL)
- **Frontend**: HTML, CSS, JavaScript
- **ODM**: PyMongo


