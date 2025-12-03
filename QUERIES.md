# MongoDB Queries Documentation - Kitabi : Library Management System

This document contains all MongoDB queries used in the Library Management System with **Embedded Documents** (NoSQL) approach.

---

## NoSQL Database Design Concepts

### Why NoSQL (MongoDB)?

This project uses **MongoDB**, a NoSQL document database, instead of traditional relational databases. Here's why:

1. **Flexible Schema**: No rigid table structures - documents can have varying fields
2. **Embedded Documents**: Related data can be stored together (denormalized)
3. **Scalability**: Horizontal scaling through sharding
4. **Performance**: Faster reads by avoiding complex joins
5. **Developer Friendly**: JSON-like documents match application objects

### Document-Oriented Design

Unlike SQL's normalized approach (separate tables with foreign keys), we use **embedded documents**:

- **Users** contain their loan history directly in a `loans` array
- **Books** contain current loans and loan history in embedded arrays
- **No separate Loans table** - loans exist within user and book documents

**Trade-offs:**
- ✅ **Pros**: Faster reads (no joins), atomic operations on single documents, data locality
- ❌ **Cons**: Data duplication (book info in user's loans), larger document sizes, harder to query across documents

### Key MongoDB Features Used

1. **Embedded Arrays**: `loans`, `current_loans`, `loan_history`, `badges`
2. **Atomic Operations**: `$push`, `$pull`, `$inc`, `$set` for concurrent-safe updates
3. **Aggregation Pipeline**: For analytics and complex queries
4. **Indexing**: On embedded array fields for performance
5. **Positional Operator (`$`)**: Update specific array elements

---

## Collections Schema

### 1. Users Collection
```json
{
  "_id": ObjectId,
  "username": "string",
  "email": "string",
  "password": "hashed_string",
  "role": "user|admin",
  "created_at": "datetime",
  "books_read": "int",
  "categories_explored": ["string"],
  "badges": [
    {
      "badge_id": "string",
      "earned_at": "datetime"
    }
  ],
  "loans": [
    {
      "loan_id": ObjectId,
      "book_id": ObjectId,
      "book_snapshot": {
        "title": "string",
        "author": "string",
        "category": "string",
        "cover_image": "string (url)"
      },
      "borrow_date": "datetime",
      "deadline": "datetime",
      "return_date": "datetime|null",
      "status": "Borrowed|Late|Returned"
    }
  ]
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

---

## User Operations

### Create User
```javascript
db.users.insertOne({
  username: "Andro",
  email: "andro@example.com",
  password: "hashed_password_here",
  role: "user",
  created_at: new Date(),
  books_read: 0,
  categories_explored: [],
  badges: [],
  loans: []
})
```

### Find User by Email
```javascript
db.users.findOne({ email: "andro@example.com" })
```

### Find User by ID
```javascript
db.users.findOne({ _id: ObjectId("user_id") })
```

### Get All Users
```javascript
db.users.find()
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

---

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
  added_at: new Date(),
  current_loans: [],
  loan_history: []
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

### Get Book by ID
```javascript
db.books.findOne({ _id: ObjectId("book_id") })
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

---

## Loan Operations (Embedded Arrays)

### Create Loan
```javascript
const loan_id = new ObjectId();
const user_id = ObjectId("user_id");
const book_id = ObjectId("book_id");

// Step 1: Get book and check availability
const book = db.books.findOne({ 
  _id: book_id,
  available_copies: { $gt: 0 }
});

// Step 2: Get user info
const user = db.users.findOne({ _id: user_id });

// Step 3: Add loan to user's loans array with book snapshot
db.users.updateOne(
  { _id: user_id },
  {
    $push: {
      loans: {
        loan_id: loan_id,
        book_id: book_id,
        book_snapshot: {
          title: book.title,
          author: book.author,
          category: book.category,
          cover_image: book.cover_image
        },
        borrow_date: new Date(),
        deadline: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000),
        return_date: null,
        status: "Borrowed"
      }
    }
  }
);

// Step 4: Add loan to book's current_loans and decrement stock
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

### Return Book
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
const book = db.books.findOne({
  _id: loan.book_id,
  "current_loans.loan_id": loan_id
});

const currentLoan = book.current_loans.find(l => l.loan_id.equals(loan_id));

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

### Get User Loans (Direct Access)
```javascript
// Simply get the user document - loans are already embedded!
const user = db.users.findOne({ _id: ObjectId("user_id") });
const userLoans = user.loans.sort((a, b) => b.borrow_date - a.borrow_date);
//On récupère un utilisateur par son _id.

/* On récupère ses prêts (loans) et on les trie du plus récent au plus ancien */
// Book info is already in book_snapshot!
```

### Get All Loans (Aggregation)
```javascript
db.users.aggregate([
  { $unwind: "$loans" },
  {
    $project: {
      user_details: {
        username: "$username",
        email: "$email",
        _id: "$_id"
      },
      loan_id: "$loans.loan_id",
      book_id: "$loans.book_id",
      book_details: "$loans.book_snapshot",
      borrow_date: "$loans.borrow_date",
      deadline: "$loans.deadline",
      return_date: "$loans.return_date",
      status: "$loans.status"
    }
  },
  { $sort: { borrow_date: -1 } }
]);
```

### Get Late Loans
```javascript
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
      user_details: {
        username: "$username",
        email: "$email",
        _id: "$_id"
      },
      loan_id: "$loans.loan_id",
      book_id: "$loans.book_id",
      book_details: "$loans.book_snapshot",
      borrow_date: "$loans.borrow_date",
      deadline: "$loans.deadline",
      return_date: "$loans.return_date",
      status: "$loans.status"
    }
  }
]);
```

### Update Loan Status
```javascript
db.users.updateOne(
  { "loans.loan_id": ObjectId("loan_id") },
  { $set: { "loans.$.status": "Late" } }
);
```

---

## Analytics & Reporting

### Count Active Loans
```javascript
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

### Loans by Category (Pie Chart Data)
```javascript
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

---

## Badge System

### Award Badge to User
```javascript
// Check if user qualifies and doesn't already have the badge
const user = db.users.findOne({ _id: ObjectId("user_id") });
const existing_badge_ids = user.badges.map(b => b.badge_id);

// Example: Award "Bookworm" badge if books_read >= 5
if (user.books_read >= 5 && !existing_badge_ids.includes("bookworm")) {
  db.users.updateOne(
    { _id: ObjectId("user_id") },
    {
      $push: {
        badges: {
          badge_id: "bookworm",
          earned_at: new Date()
        }
      }
    }
  );
}
```

### Get User Badges
```javascript
const user = db.users.findOne({ _id: ObjectId("user_id") });
const badges = user.badges || [];
// Map badge_id to badge definitions in application logic
```

### Initialize User Badge Fields
```javascript
db.users.updateOne(
  { _id: ObjectId("user_id") },
  { 
    $set: { 
      badges: [], 
      books_read: 0, 
      categories_explored: [] 
    } 
  }
);
```

---

## Best Practices

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
- **$unwind**: Flatten array in aggregation

### Atomic Operations
Always use atomic operators for consistency:
- ✅ **GOOD**: `{ $inc: { available_copies: -1 } }`
- ✅ **GOOD**: `{ $push: { loans: {...} } }`
- ❌ **BAD**: Read → Calculate → Write (race condition risk)

---

## Business Rules Implementation

### One Book Per User Rule
```javascript
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

---

## Security Best Practices

1. **Validate user identity** before modifying loan arrays
2. **Use atomic operations** for all array modifications
3. **Index array fields** for performance
4. **Check business rules** before adding to arrays
5. **Use positional $ operator** carefully to update correct array element
6. **Never store passwords in plain text** - always hash with bcrypt/argon2