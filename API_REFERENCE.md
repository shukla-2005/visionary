# API Endpoints Reference - Stock Predictions

## Base URL
```
http://localhost:8000
```

## Authentication
All endpoints (except `/auth/*`) require JWT token in header:
```
Authorization: Bearer <your_token>
```

---

## Authentication Endpoints

### Register User
```
POST /auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password"
}

Response (201):
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com"
}
```

### Login
```
POST /auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password"
}

Response (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

## Stock Data Endpoints

### Search Stock
```
GET /stocks/search/{ticker}

Response (200):
{
  "ticker": "AAPL",
  "name": "Apple Inc.",
  "sector": "Technology",
  "market_cap": 2800000000000,
  "current_price": 150.25,
  "week_52_high": 199.62,
  "week_52_low": 124.17,
  "average_volume": 52384000
}
```

### Get Historical Data
```
GET /stocks/history/{ticker}?period=1y

Parameters:
  - ticker: Stock symbol (required)
  - period: Time period (default: 1y)
    Options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max

Response (200): Array of historical data
[
  {
    "date": "2024-04-07",
    "open": 149.50,
    "high": 151.00,
    "low": 149.00,
    "close": 150.25,
    "volume": 45000000,
    "adj_close": 150.25
  },
  ...
]
```

### Get Technical Indicators
```
GET /stocks/indicators/{ticker}?period=1y

Response (200): Array of technical indicators
[
  {
    "date": "2024-04-07",
    "sma_20": 148.50,
    "sma_50": 147.25,
    "ema_12": 149.75,
    "ema_26": 148.90,
    "macd": 0.85,
    "rsi": 65.25,
    "bollinger_upper": 155.00,
    "bollinger_middle": 150.00,
    "bollinger_lower": 145.00
  },
  ...
]
```

### Stock Analysis
```
GET /stocks/analysis/{ticker}?period=1y

Response (200):
{
  "ticker": "AAPL",
  "info": { /* StockInfo */ },
  "historical_data": [ /* HistoricalData[] */ ],
  "indicators": [ /* TechnicalIndicators[] */ ]
}
```

### Compare Stocks
```
POST /stocks/compare
Content-Type: application/json

{
  "tickers": ["AAPL", "MSFT", "GOOGL"],
  "period": "1y"
}

Response (200):
{
  "tickers": ["AAPL", "MSFT", "GOOGL"],
  "data": {
    "AAPL": { /* comparison data */ },
    "MSFT": { /* comparison data */ },
    "GOOGL": { /* comparison data */ }
  }
}
```

---

## ML Model Training Endpoints

### Train Models
```
POST /models/train/{ticker}
Content-Type: application/json

{
  "ticker": "AAPL",
  "models": ["linear", "rf", "xgb", "lstm"]
}

Response (200):
{
  "ticker": "AAPL",
  "trained_models": ["linear", "rf", "xgb", "lstm"],
  "best_model": "xgb",
  "metrics": {
    "linear": {
      "rmse": 5.23,
      "mae": 3.45,
      "r2_score": 0.87,
      "mape": 2.15
    },
    "rf": { /* metrics */ },
    "xgb": { /* metrics */ },
    "lstm": { /* metrics */ }
  }
}
```

### Compare Models
```
GET /models/compare/{ticker}

Response (200):
[
  {
    "model_name": "linear",
    "metrics": { /* ModelMetrics */ },
    "best_model": false
  },
  {
    "model_name": "lstm",
    "metrics": { /* ModelMetrics */ },
    "best_model": true
  },
  ...
]
```

---

## Prediction Endpoints (New Features)

### Single Model Prediction
```
POST /models/predict/{ticker}
Content-Type: application/json

{
  "model_name": "lstm",
  "days_ahead": 7
}

Response (200):
{
  "ticker": "AAPL",
  "model_name": "lstm",
  "predicted_price": 150.25,
  "prediction_date": "2024-04-07T10:30:00Z",
  "days_ahead": 7
}
```

### Ensemble Prediction ⭐ NEW
```
POST /models/ensemble/{ticker}
Content-Type: application/json

{
  "model_name": "ensemble",
  "days_ahead": 7
}

Response (200):
{
  "ensemble_prediction": 150.25,
  "std_deviation": 3.42,
  "lower_bound": 146.83,
  "upper_bound": 153.67,
  "model_predictions": {
    "linear": {
      "price": 149.50,
      "weight": 0.25
    },
    "rf": {
      "price": 151.00,
      "weight": 0.25
    },
    "xgb": {
      "price": 150.75,
      "weight": 0.25
    },
    "lstm": {
      "price": 150.00,
      "weight": 0.25
    }
  },
  "num_models": 4
}
```

### Confidence Interval Prediction ⭐ NEW
```
POST /models/confidence/{ticker}
Content-Type: application/json

{
  "model_name": "lstm",
  "days_ahead": 7
}

Response (200):
{
  "prediction": 150.25,
  "lower_bound": 145.30,
  "upper_bound": 155.20,
  "confidence_level": 0.95,
  "confidence_range": 4.95,
  "volatility_based": true
}
```

### Future Price Forecast ⭐ NEW
```
POST /models/forecast/{ticker}?days=30
Content-Type: application/json

{
  "model_name": "lstm",
  "days_ahead": 30
}

Response (200):
{
  "ticker": "AAPL",
  "current_price": 150.00,
  "forecast": [
    {
      "date": "2024-04-08",
      "predicted_price": 150.50,
      "days_ahead": 1,
      "lower_bound": 147.99,
      "upper_bound": 153.01,
      "confidence": 0.95
    },
    {
      "date": "2024-04-09",
      "predicted_price": 151.00,
      "days_ahead": 2,
      "lower_bound": 147.40,
      "upper_bound": 154.60,
      "confidence": 0.95
    },
    // ... 28 more days
  ],
  "start_date": "2024-04-07",
  "end_date": "2024-05-07",
  "model": "lstm"
}
```

### Batch Predictions for Multiple Stocks ⭐ NEW
```
POST /models/predict-batch
Content-Type: application/json

{
  "tickers": ["AAPL", "MSFT", "GOOGL", "TSLA"],
  "model_name": "lstm",
  "days_ahead": 7
}

Response (200):
{
  "tickers": ["AAPL", "MSFT", "GOOGL", "TSLA"],
  "model_name": "lstm",
  "days_ahead": 7,
  "predictions": {
    "AAPL": {
      "success": true,
      "prediction": 150.25,
      "days_ahead": 7,
      "prediction_date": "2024-04-07T10:30:00Z"
    },
    "MSFT": {
      "success": true,
      "prediction": 428.75,
      "days_ahead": 7,
      "prediction_date": "2024-04-07T10:30:00Z"
    },
    "GOOGL": {
      "success": true,
      "prediction": 155.30,
      "days_ahead": 7,
      "prediction_date": "2024-04-07T10:30:00Z"
    },
    "TSLA": {
      "success": true,
      "prediction": 245.60,
      "days_ahead": 7,
      "prediction_date": "2024-04-07T10:30:00Z"
    }
  }
}
```

---

## Prediction History Endpoints

### Get Prediction History
```
GET /history

Response (200):
[
  {
    "id": 1,
    "user_id": 1,
    "ticker": "AAPL",
    "model_name": "lstm",
    "predicted_price": 150.25,
    "prediction_date": "2024-04-07T10:30:00Z",
    "days_ahead": 7,
    "actual_price": null,
    "created_at": "2024-04-07T10:30:00Z"
  },
  ...
]
```

---

## Report Endpoints

### Generate Report
```
GET /report/{ticker}?format=csv

Parameters:
  - ticker: Stock symbol (required)
  - format: csv or pdf (default: csv)

Response (200): File download
Content-Type: text/csv or application/pdf
```

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Codes

| Code | Message | Solution |
|------|---------|----------|
| 400 | Bad Request | Check request format and parameters |
| 401 | Unauthorized | Provide valid JWT token |
| 404 | Not Found | Stock or resource doesn't exist |
| 500 | Server Error | Insufficient data or model not trained |

---

## Rate Limiting

- No strict rate limiting in development
- Production should implement rate limiting
- Default: No token expiration

---

## Response Models

### StockInfo
```json
{
  "ticker": "AAPL",
  "name": "Apple Inc.",
  "sector": "Technology",
  "market_cap": 2800000000000,
  "current_price": 150.25,
  "week_52_high": 199.62,
  "week_52_low": 124.17,
  "average_volume": 52384000
}
```

### PredictionResponse
```json
{
  "ticker": "AAPL",
  "model_name": "lstm",
  "predicted_price": 150.25,
  "prediction_date": "2024-04-07T10:30:00Z",
  "days_ahead": 7,
  "confidence_interval": {
    "lower_bound": 145.30,
    "upper_bound": 155.20,
    "confidence_level": 0.95
  }
}
```

### ModelMetrics
```json
{
  "rmse": 5.23,
  "mae": 3.45,
  "r2_score": 0.87,
  "mape": 2.15
}
```

---

## Quick Examples

### Example 1: Get Prediction with Confidence
```bash
curl -X POST http://localhost:8000/models/confidence/AAPL \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "lstm",
    "days_ahead": 7
  }'
```

### Example 2: Predict Multiple Stocks
```bash
curl -X POST http://localhost:8000/models/predict-batch \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["AAPL", "MSFT", "GOOGL"],
    "model_name": "lstm",
    "days_ahead": 7
  }'
```

### Example 3: Generate 30-Day Forecast
```bash
curl -X POST "http://localhost:8000/models/forecast/AAPL?days=30" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "lstm",
    "days_ahead": 30
  }'
```

---

## Swagger/OpenAPI Documentation

Full interactive API documentation available at:
- **Development**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

Use the Swagger UI to test all endpoints interactively!

---

*Last Updated: April 2024*
*API Version: 1.2.0*
