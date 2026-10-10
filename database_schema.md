# Database Schema

## Overview
The application uses SQLite by default, but can be configured to use PostgreSQL for production.

## Tables

### users
Stores user authentication information.

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

**Fields:**
- `id`: Primary key, auto-increment
- `username`: Unique username for login
- `email`: Unique email address
- `hashed_password`: Bcrypt hashed password
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp

### prediction_history
Stores user's prediction history.

```sql
CREATE TABLE prediction_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    ticker VARCHAR NOT NULL,
    model_name VARCHAR NOT NULL,
    predicted_price FLOAT NOT NULL,
    prediction_date DATETIME NOT NULL,
    days_ahead INTEGER NOT NULL,
    actual_price FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**Fields:**
- `id`: Primary key, auto-increment
- `user_id`: Foreign key to users table
- `ticker`: Stock ticker symbol
- `model_name`: ML model used (linear, rf, xgb, lstm)
- `predicted_price`: Predicted stock price
- `prediction_date`: Date for which prediction was made
- `days_ahead`: Number of days ahead the prediction is for
- `actual_price`: Actual price (filled later if available)
- `created_at`: Record creation timestamp

## Indexes

```sql
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_prediction_history_user_id ON prediction_history(user_id);
CREATE INDEX idx_prediction_history_ticker ON prediction_history(ticker);
CREATE INDEX idx_prediction_history_created_at ON prediction_history(created_at);
```

## Relationships

- `prediction_history.user_id` → `users.id` (Many-to-One)

## Data Types

- `INTEGER`: SQLite integer type
- `VARCHAR`: Variable-length string
- `FLOAT`: Floating-point number
- `TIMESTAMP/DATETIME`: Date and time
- `AUTOINCREMENT`: Auto-incrementing primary key

## PostgreSQL Migration

For PostgreSQL, the schema would be:

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Prediction history table
CREATE TABLE prediction_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    ticker VARCHAR(10) NOT NULL,
    model_name VARCHAR(20) NOT NULL,
    predicted_price DECIMAL(10,2) NOT NULL,
    prediction_date TIMESTAMP WITH TIME ZONE NOT NULL,
    days_ahead INTEGER NOT NULL,
    actual_price DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_prediction_history_user_id ON prediction_history(user_id);
CREATE INDEX idx_prediction_history_ticker ON prediction_history(ticker);
CREATE INDEX idx_prediction_history_created_at ON prediction_history(created_at);
```

## Sample Data

### Users
```sql
INSERT INTO users (username, email, hashed_password) VALUES
('demo_user', 'demo@example.com', '$2b$12$hashedpasswordhere');
```

### Prediction History
```sql
INSERT INTO prediction_history (user_id, ticker, model_name, predicted_price, prediction_date, days_ahead) VALUES
(1, 'AAPL', 'lstm', 150.25, '2024-01-15 10:00:00', 7);
```

## Backup Strategy

- SQLite: Copy the `.db` file
- PostgreSQL: Use `pg_dump` for logical backups

## Performance Considerations

- Indexes on frequently queried columns (username, email, user_id, ticker)
- Consider partitioning prediction_history by date if it grows large
- Use connection pooling in production
- Implement database migrations for schema changes