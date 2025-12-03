# MongoDB Queries Documentation - Library Management System

This document contains all MongoDB queries used in the Library Management System with **Nested Collections** approach.

## Collections Schema

### 1. Users Collection (with Embedded Loans)
```json
{
  "_id": ObjectId,
  "username": "string",
  "email": "string",
  "password": "hashed_string",
}
```

### 2. Books Collection (with Embedded Loans)
```json
{
  "_id": ObjectId,
  "title": "string",
  "author": "string",
  "category": "string",
  "description": "string",
  "cover_image": "string (url)",
  "total_copies": "int",
  "available_copies": "int",
  "added_at": "datetime",
  "current_loans": [
    {
      "loan_id": ObjectId,
      "user_id": ObjectId,
      "user_name": "string",
      "borrow_date": "datetime",
      "deadline": "datetime",
      "status": "Borrowed|Late"
    }
  ],
  "loan_history": [
    {
      "loan_id": ObjectId,
      "user_id": ObjectId,
      "user_name": "string",
      "borrow_date": "datetime",
      "return_date": "datetime",
      "status": "Returned"
    }
  ]
}
```

### 3. Note on Loans
**Loans are now embedded within user and book documents.** There is no separate loans collection. This is a document-oriented approach where:
- User documents contain their loan history in the `loans` array
- Book documents contain current loans in `current_loans` array and history in `loan_history` array

## User Operations

### Create User (with Empty Loans Array)
```javascript
db.users.insertOne({
  username: "Andro",
  email: "Andro@example.com",
  password: "hashed_password_here",
  role: "user",
  created_at: new Date(),
  loans: []  // Initialize empty array
})
```

### Find User by Email
```javascript
db.users.findOne({ email: "Ali@example.com" })
```

### Find User by Username
```javascript
db.users.findOne({ username: "Farah" })
```

### Update User
```javascript
db.users.updateOne(
  { _id: ObjectId("user_id") },
  { $set: { username: "new_name" } }
)
```

### Delete User
```javascript
db.users.deleteOne({ _id: ObjectId("user_id") })
```

## Book Operations

### Add Book (with Empty Loan Arrays)
```javascript
db.books.insertOne({
  title: "The Great Gatsby",
  author: "F. Scott Fitzgerald",
  category: "Classic",
  description: "A novel about the American Dream",
  cover_image: "https://example.com/cover.jpg",
  total_copies: 10,
  available_copies: 10,
  added_at: new Date(),
  current_loans: [],    // Initialize empty
  loan_history: []      // Initialize empty
})
```

### Search Books (Case-Insensitive)
```javascript
db.books.find({
  $or: [
    { title: { $regex: "gatsby", $options: "i" } },
    { author: { $regex: "gatsby", $options: "i" } },
    { category: { $regex: "gatsby", $options: "i" } }
  ]
})
```

### Filter Books by Category
```javascript
db.books.find({ category: "Classic" })
```

### Get All Categories (Distinct)
```javascript
db.books.distinct("category")
```

### Update Book
```javascript
db.books.updateOne(
  { _id: ObjectId("book_id") },
  { 
    $set: { 
      title: "Updated Title",
      total_copies: 15
    } 
  }
)
```

### Delete Book
```javascript
db.books.deleteOne({ _id: ObjectId("book_id") })
```

## Loan Operations (Embedded Arrays)

### Create Loan - Add to User and Book
```javascript
const loan_id = new ObjectId();
const user_id = ObjectId("user_id");
const book_id = ObjectId("book_id");

// Step 1: Get book and user info
const book = db.books.findOne({ 
  _id: book_id,
  available_copies: { $gt: 0 }
});

const user = db.users.findOne({ _id: user_id });

// Step 2: Add loan to user's loans array
db.users.updateOne(
      }
    }
  }
);

// Step 3: Add loan to book's current_loans and decrement stock
db.books.updateOne(
  { _id: book_id },
  {
    $push: {
      current_loans: {
        loan_id: loan_id,
        user_id: user_id,
        user_name: user.username,
        borrow_date: new Date(),
        deadline: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000),
        status: "Borrowed"
      }
    },
    $inc: { available_copies: -1 }
  }
);
```

### Return Book - Update User and Book
```javascript
const loan_id = ObjectId("loan_id");

// Step 1: Find user with this loan
const user = db.users.findOne({
  "loans.loan_id": loan_id
});

const loan = user.loans.find(l => l.loan_id.equals(loan_id));

// Step 2: Update loan status in user's loans array
db.users.updateOne(
  {
    _id: user._id,
    "loans.loan_id": loan_id
  },
  {
    $set: {
      "loans.$.return_date": new Date(),
      "loans.$.status": "Returned"
    }
  }
);

// Step 3: Find the current loan in book
const bookWithLoan = db.books.findOne({
  _id: loan.book_id,
  "current_loans.loan_id": loan_id
});

const currentLoan = bookWithLoan.current_loans.find(l => l.loan_id.equals(loan_id));

// Step 4: Move from current_loans to loan_history
db.books.updateOne(
  { _id: loan.book_id },
  {
    $pull: { current_loans: { loan_id: loan_id } },
    $push: {
      loan_history: {
        loan_id: currentLoan.loan_id,
        user_id: currentLoan.user_id,
        user_name: currentLoan.user_name,
        borrow_date: currentLoan.borrow_date,
        return_date: new Date(),
        status: "Returned"
      }
    },
    $inc: { available_copies: 1 }
  }
);
```

### Check if User Has Active Loan
```javascript
// Using $elemMatch to find active loans in embedded array
const user = db.users.findOne({
  _id: ObjectId("user_id"),
  loans: {
    $elemMatch: {
      status: { $in: ["Borrowed", "Late"] }
    }
  }
});
// Returns null if no active loan, user document if has active loan
```

### Get User Loans (Direct Access - No Aggregation!)
```javascript
// Simply get the user document - loans are already embedded!
const user = db.users.findOne({ _id: ObjectId("user_id") });
const userLoans = user.loans.sort((a, b) => b.borrow_date - a.borrow_date);
// Book info is already in book_snapshot!
```

### Get All Active Loans (From Books)
```javascript
// Query books with current_loans
db.books.aggregate([
  { $match: { current_loans: { $exists: true, $ne: [] } } },
  { $unwind: "$current_loans" },
  {
    $project: {
      title: 1,
      author: 1,
      category: 1,
      loan: "$current_loans"
    }
  }
]);
```

### Get Late Loans
```javascript
// From users - find users with late loans
db.users.aggregate([
  { $unwind: "$loans" },
  { 
    $match: {
      "loans.status": { $in: ["Borrowed", "Late"] },
      "loans.deadline": { $lt: new Date() }
    }
  },
  {
    $project: {
      username: 1,
      email: 1,
      loan: "$loans"
    }
  }
]);
```

## Analytics & Reporting

### Count Active Loans
```javascript
// Count all users with active loans
db.users.aggregate([
  { $unwind: "$loans" },
  {
    $match: {
      "loans.status": { $in: ["Borrowed", "Late"] }
    }
  },
  { $count: "active_loans" }
]);
```

### Loans by Category
```javascript
// From users' loan history
db.users.aggregate([
  { $unwind: "$loans" },
  {
    $group: {
      _id: "$loans.book_snapshot.category",
      count: { $sum: 1 }
    }
  },
  { $sort: { count: -1 } }
]);

// OR from books' loan history
db.books.aggregate([
  {
    $project: {
      category: 1,
      total_loans: {
        $add: [
          { $size: { $ifNull: ["$current_loans", []] } },
          { $size: { $ifNull: ["$loan_history", []] } }
        ]
      }
    }
  },
  {
    $group: {
      _id: "$category",
      count: { $sum: "$total_loans" }
    }
  },
  { $sort: { count: -1 } }
]);
```

### Loans by Month (Current Year)
```javascript
db.users.aggregate([
  { $unwind: "$loans" },
  { 
    $match: {
      "loans.borrow_date": { 
        $gte: new Date(new Date().getFullYear(), 0, 1) 
      }
    } 
  },
  { 
    $group: {
      _id: { $month: "$loans.borrow_date" },
      count: { $sum: 1 }
    } 
  },
  { $sort: { _id: 1 } }
]);
```

### Loan Status Distribution
```javascript
db.users.aggregate([
  { $unwind: "$loans" },
  { 
    $group: {
      _id: "$loans.status",
      count: { $sum: 1 }
    } 
  }
]);
```

## Best Practices for Embedded Documents

### Indexing for Performance
```javascript
// Users
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ "loans.status": 1 });
db.users.createIndex({ "loans.loan_id": 1 });

// Books
db.books.createIndex({ title: 1 });
db.books.createIndex({ category: 1 });
db.books.createIndex({ "current_loans.loan_id": 1 });
db.books.createIndex({ "current_loans.user_id": 1 });
```

### Array Operations
Key operators for embedded arrays:
- **$push**: Add new element to array
- **$pull**: Remove element from array  
- **$set with positional $**: Update specific array element
- **$elemMatch**: Query elements in array
- **$unwind**: Flatten array in aggre

gation

### Atomic Operations
Always use atomic operators for consistency:
- **GOOD**: `{ $inc: { available_copies: -1 } }`
- **GOOD**: `{ $push: { loans: {...} } }`
- **BAD**: Read → Calculate → Write

## Business Rules Implementation

### One Book Per User Rule
```javascript
// Check user's loans array for active loans
const user = db.users.findOne({
  _id: ObjectId("user_id"),
  loans: {
    $elemMatch: {
      status: { $in: ["Borrowed", "Late"] }
    }
  }
});

if (user) {
  // Reject: User already has an active book
} else {
  // Allow: User can borrow a book
}
```

### Data Consistency
When creating/updating loans, always update BOTH:
1. User's `loans` array (with book_snapshot)
2. Book's `current_loans` or `loan_history` array (with user_name)

### Document Size Limits
MongoDB documents have a 16MB limit. Monitor:
- User documents with extensive loan history
- Books with many loans

Consider archiving old loan history if needed.

## Security Best Practices

1. **Validate user identity** before modifying loan arrays
2. **Use atomic operations** for all array modifications
3. **Index array fields** for performance (loans.loan_id, current_loans.user_id)
4. **Check business rules** before adding to arrays
5. **Use positional $ operator** carefully to update correct array element