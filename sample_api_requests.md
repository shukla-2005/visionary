# Sample API Requests

This document provides sample API requests for testing the Stock Market Analysis API.

## Base URL
```
http://localhost:8000
```

For the deployed API, use <https://stock-analysis-api-0dqg.onrender.com>. The
examples in this file target a locally running backend; replace the base URL
when testing against Render.

## Authentication

### Register User
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

## Stock Endpoints

### Search Stock
```bash
curl -X GET "http://localhost:8000/stocks/search/AAPL"
```

Response:
```json
{
  "ticker": "AAPL",
  "name": "Apple Inc.",
  "sector": "Technology",
  "market_cap": 2500000000000,
  "current_price": 150.25,
  "week_52_high": 199.62,
  "week_52_low": 124.17,
  "average_volume": 50000000
}
```

### Get Historical Data
```bash
curl -X GET "http://localhost:8000/stocks/history/AAPL?period=1y"
```

### Get Technical Indicators
```bash
curl -X GET "http://localhost:8000/stocks/indicators/AAPL?period=1y"
```

### Compare Stocks
```bash
curl -X POST "http://localhost:8000/stocks/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["AAPL", "MSFT", "GOOGL"],
    "period": "1y"
  }'
```

### Get Top Movers
```bash
curl -X GET "http://localhost:8000/stocks/top-movers"
```

### Get Sector Analysis
```bash
curl -X GET "http://localhost:8000/stocks/sector-analysis"
```

## Model Endpoints

### Train Models (Requires Authentication)
```bash
curl -X POST "http://localhost:8000/models/train/AAPL" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "models": ["linear", "rf", "xgb", "lstm"]
  }'
```

### Make Prediction (Requires Authentication)
```bash
curl -X POST "http://localhost:8000/predict/AAPL" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "lstm",
    "days_ahead": 7
  }'
```

### Get Prediction History (Requires Authentication)
```bash
curl -X GET "http://localhost:8000/history" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Report Generation (Requires Authentication)

### Generate CSV Report
```bash
curl -X GET "http://localhost:8000/report/AAPL?format=csv" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o AAPL_report.csv
```

### Generate PDF Report
```bash
curl -X GET "http://localhost:8000/report/AAPL?format=pdf" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o AAPL_report.pdf
```

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Stock not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error message"
}
```

## Testing with Python

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# Register user
register_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
}
response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
print("Register:", response.json())

# Login
login_data = {
    "username": "testuser",
    "password": "password123"
}
response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get stock info
response = requests.get(f"{BASE_URL}/stocks/search/AAPL")
print("Stock Info:", response.json())

# Train model
train_data = {"models": ["linear", "rf"]}
response = requests.post(f"{BASE_URL}/models/train/AAPL", json=train_data, headers=headers)
print("Training:", response.json())

# Make prediction
predict_data = {"model_name": "rf", "days_ahead": 7}
response = requests.post(f"{BASE_URL}/predict/AAPL", json=predict_data, headers=headers)
print("Prediction:", response.json())
```