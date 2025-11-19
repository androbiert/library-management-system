# MongoDB Queries Documentation - Library Management System

This document contains all MongoDB queries used in the Library Management System, demonstrating NoSQL best practices.

## Collections Schema

### 1. Users Collection
```json
{
  "_id": ObjectId,
  "username": "string",
  "email": "string",
  "password": "hashed_string",
  "role": "admin|user",
  "created_at": "datetime"
}
```

### 2. Books Collection
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
  "added_at": "datetime"
}
```

### 3. Loans Collection
```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "book_id": ObjectId,
  "borrow_date": "datetime",
  "deadline": "datetime",
  "return_date": "datetime (nullable)",
  "status": "Borrowed|Returned|Late|Lost"
}
```

## User Operations

### Create User
```javascript
db.users.insertOne({
  username: "john_doe",
  email: "john@example.com",
  password: "hashed_password_here",
  role: "user",
  created_at: new Date()
})
```

### Find User by Email
```javascript
db.users.findOne({ email: "john@example.com" })
```

### Find User by Username
```javascript
db.users.findOne({ username: "john_doe" })
```

### Find User by Username OR Email (Flexible Login)
```javascript
// Check if input contains @ to determine if it's email or username
const input = "john@example.com"; // or "john_doe"
const isEmail = input.includes("@");

db.users.findOne(
  isEmail ? { email: input } : { username: input }
)
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

### Add Book
```javascript
db.books.insertOne({
  title: "The Great Gatsby",
  author: "F. Scott Fitzgerald",
  category: "Classic",
  description: "A novel about the American Dream",
  cover_image: "https://example.com/cover.jpg",
  total_copies: 10,
  available_copies: 10,
  added_at: new Date()
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

## Loan Operations

### Create Loan (with Atomic Stock Decrement)
```javascript
// Step 1: Check availability
const book = db.books.findOne({ 
  _id: ObjectId("book_id"),
  available_copies: { $gt: 0 }
})

// Step 2: Create loan
db.loans.insertOne({
  user_id: ObjectId("user_id"),
  book_id: ObjectId("book_id"),
  borrow_date: new Date(),
  deadline: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000), // 14 days
  return_date: null,
  status: "Borrowed"
})

// Step 3: Atomic decrement (ensures no race conditions)
db.books.updateOne(
  { _id: ObjectId("book_id") },
  { $inc: { available_copies: -1 } }
)
```

### Return Book (with Atomic Stock Increment)
```javascript
// Update loan status
db.loans.updateOne(
  { _id: ObjectId("loan_id") },
  { 
    $set: { 
      return_date: new Date(),
      status: "Returned"
    } 
  }
)

// Atomic increment
db.books.updateOne(
  { _id: ObjectId("book_id") },
  { $inc: { available_copies: 1 } }
)
```

### Check if User Has Active Loan (One Book Per User)
```javascript
// Check if user already has an active book
db.loans.findOne({
  user_id: ObjectId("user_id"),
  status: { $in: ["Borrowed", "Late"] }
})
// Returns null if no active loan, document if user has active book
```

### User Self-Return Book (with Verification)
```javascript
// Step 1: Verify loan belongs to user
const loan = db.loans.findOne({
  _id: ObjectId("loan_id"),
  user_id: ObjectId("user_id") // Security check
})

if (loan) {
  // Step 2: Update loan status
  db.loans.updateOne(
    { _id: ObjectId("loan_id") },
    { 
      $set: { 
        return_date: new Date(),
        status: "Returned"
      } 
    }
  )
  
  // Step 3: Increment book stock
  db.books.updateOne(
    { _id: loan.book_id },
    { $inc: { available_copies: 1 } }
  )
}
```

### Get User Loans (with Book Details)
```javascript
db.loans.aggregate([
  { $match: { user_id: ObjectId("user_id") } },
  { 
    $lookup: {
      from: "books",
      localField: "book_id",
      foreignField: "_id",
      as: "book_details"
    }
  },
  { $unwind: "$book_details" },
  { $sort: { borrow_date: -1 } }
])
```

### Get All Loans (with User and Book Details)
```javascript
db.loans.aggregate([
  { 
    $lookup: {
      from: "users",
      localField: "user_id",
      foreignField: "_id",
      as: "user_details"
    }
  },
  { $unwind: "$user_details" },
  { 
    $lookup: {
      from: "books",
      localField: "book_id",
      foreignField: "_id",
      as: "book_details"
    }
  },
  { $unwind: "$book_details" },
  { $sort: { borrow_date: -1 } }
])
```

### Get Late Loans
```javascript
db.loans.aggregate([
  { 
    $match: { 
      status: { $in: ["Borrowed", "Late"] },
      deadline: { $lt: new Date() }
    } 
  },
  { 
    $lookup: {
      from: "users",
      localField: "user_id",
      foreignField: "_id",
      as: "user_details"
    }
  },
  { $unwind: "$user_details" },
  { 
    $lookup: {
      from: "books",
      localField: "book_id",
      foreignField: "_id",
      as: "book_details"
    }
  },
  { $unwind: "$book_details" }
])
```

## Analytics & Reporting

### Count Active Loans
```javascript
db.loans.countDocuments({
  status: { $in: ["Borrowed", "Late"] }
})
```

### Loans by Category
```javascript
db.loans.aggregate([
  { 
    $lookup: {
      from: "books",
      localField: "book_id",
      foreignField: "_id",
      as: "book_details"
    }
  },
  { $unwind: "$book_details" },
  { 
    $group: {
      _id: "$book_details.category",
      count: { $sum: 1 }
    } 
  },
  { $sort: { count: -1 } }
])
```

### Loans by Month (Current Year)
```javascript
db.loans.aggregate([
  { 
    $match: {
      borrow_date: { 
        $gte: new Date(new Date().getFullYear(), 0, 1) 
      }
    } 
  },
  { 
    $group: {
      _id: { $month: "$borrow_date" },
      count: { $sum: 1 }
    } 
  },
  { $sort: { _id: 1 } }
])
```

### Loan Status Distribution
```javascript
db.loans.aggregate([
  { 
    $group: {
      _id: "$status",
      count: { $sum: 1 }
    } 
  }
])
```

## Best Practices

### Indexing for Performance
```javascript
// Users
db.users.createIndex({ email: 1 }, { unique: true })

// Books
db.books.createIndex({ title: 1 })
db.books.createIndex({ category: 1 })

// Loans
db.loans.createIndex({ user_id: 1 })
db.loans.createIndex({ book_id: 1 })
db.loans.createIndex({ status: 1 })
db.loans.createIndex({ deadline: 1 })
```

### Atomic Operations
Always use `$inc` for stock management to prevent race conditions:
- **BAD**: Read → Calculate → Write
- **GOOD**: `{ $inc: { available_copies: -1 } }`

### Aggregation Pipeline
Use aggregation pipelines for complex queries with joins:
- `$lookup` for joining collections
- `$match` for filtering
- `$group` for aggregations
- `$sort` for ordering

## Business Rules Implementation

### One Book Per User Rule
Always check for active loans before creating a new loan:
```javascript
const activeLoan = db.loans.findOne({
  user_id: ObjectId("user_id"),
  status: { $in: ["Borrowed", "Late"] }
})

if (activeLoan) {
  // Reject: User already has an active book
} else {
  // Allow: User can borrow a book
}
```

### User Permission Verification
For user self-return, always verify ownership:
```javascript
// GOOD: Verify loan belongs to user
const loan = db.loans.findOne({
  _id: ObjectId("loan_id"),
  user_id: ObjectId("current_user_id")
})

// BAD: Trust client-side data without verification
```

## Security Best Practices

1. **Always validate user identity** before allowing returns
2. **Use atomic operations** for all stock management
3. **Index foreign keys** (user_id, book_id) for performance
4. **Check business rules** (one book per user) before transactions

