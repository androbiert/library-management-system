# Library Management System

A complete Library Management System using Flask and MongoDB.

## Features
- **Admin Dashboard**: Manage books, users, and loans.
- **User Interface**: Browse books, view loan history.
- **NoSQL Database**: MongoDB with optimized schema.

## Setup

1.  **Prerequisites**:
    -   Python 3.x
    -   MongoDB installed and running locally on port 27017.

2.  **Installation**:
    ```bash
    cd library_system
    pip install -r requirements.txt
    ```

3.  **Running the Application**:
    ```bash
    python app.py
    ```
    The application will be available at `http://127.0.0.1:5000`.

## Usage

### Admin Account
-   Register a new account and select "Admin" as the role.
-   Or use the test script to create a default admin.

### User Account
-   Register a new account and select "User" as the role.

## NoSQL Queries
Check `utils/queries.py` to see the implementation of NoSQL operations.
