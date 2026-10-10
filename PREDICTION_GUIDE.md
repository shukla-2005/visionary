# Stock Price Prediction Guide

## Overview

The Visionary stock prediction system provides multiple advanced methods to forecast future stock prices using machine learning. This guide covers all prediction features and how to use them effectively.

## Prediction Methods

### 1. Single Model Predictions

**Best for**: Quick, single-day predictions using a specific model

**Process**:
1. Select a stock ticker (e.g., AAPL)
2. Choose a model (Linear, Random Forest, XGBoost, or LSTM)
3. Train the model on historical data
4. Make predictions for 7, 15, or 30 days ahead

**API**:
```bash
POST /models/predict/{ticker}
{
  "model_name": "lstm",
  "days_ahead": 7
}
```

**Python**:
```python
from ml.predict import make_prediction

price = make_prediction("AAPL", "lstm", days_ahead=7)
```

**Expected Output**: Single predicted price value

---

### 2. Ensemble Predictions

**Best for**: More robust predictions that combine multiple models' strengths

**How It Works**:
- Trains 4 different ML models (Linear, RF, XGBoost, LSTM)
- Averages their predictions for a consensus forecast
- Calculates standard deviation for uncertainty
- Provides confidence ranges

**API**:
```bash
POST /models/ensemble/{ticker}
{
  "model_name": "ensemble",
  "days_ahead": 7
}
```

Response:
```json
{
  "ensemble_prediction": 150.25,
  "std_deviation": 3.42,
  "lower_bound": 146.83,
  "upper_bound": 153.67,
  "model_predictions": {
    "linear": {"price": 149.50, "weight": 0.25},
    "rf": {"price": 151.00, "weight": 0.25},
    "xgb": {"price": 150.75, "weight": 0.25},
    "lstm": {"price": 150.00, "weight": 0.25}
  },
  "num_models": 4
}
```

**Python**:
```python
from ml.predict import predict_with_ensemble

result = predict_with_ensemble("AAPL", models=["linear", "rf", "xgb", "lstm"], days_ahead=7)
```

**Advantages**:
- Reduces individual model bias
- Standard deviation shows prediction confidence
- Better for risk management

---

### 3. Multi-Day Sequential Forecasting

**Best for**: Understanding price trends and momentum over 30+ days

**How It Works**:
- Uses recursive prediction where each day's forecast becomes input for the next
- Captures market momentum more realistically
- Supports any of the 4 ML models

**API**:
```bash
POST /models/forecast/{ticker}?days=30
{
  "model_name": "lstm",
  "days_ahead": 30
}
```

Response:
```json
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
    // ... 29 more days
  ],
  "start_date": "2024-04-07",
  "end_date": "2024-05-07",
  "model": "lstm"
}
```

**Python**:
```python
from ml.predict import get_future_price_forecast

forecast = get_future_price_forecast("AAPL", "lstm", days=30)
```

**Use Cases**:
- Investment planning
- Risk assessment over time
- Trend identification

---

### 4. Confidence Intervals

**Best for**: Understanding prediction uncertainty

**How It Works**:
- Calculates volatility from historical data
- Adjusts confidence ranges based on time horizon
- Provides statistical bounds for predictions

**API**:
```bash
POST /models/confidence/{ticker}
{
  "model_name": "lstm",
  "days_ahead": 7
}
```

Response:
```json
{
  "prediction": 150.25,
  "lower_bound": 145.30,
  "upper_bound": 155.20,
  "confidence_level": 0.95,
  "confidence_range": 4.95,
  "volatility_based": true
}
```

**Interpretation**:
- **Narrow range**: More confident prediction
- **Wide range**: More uncertainty (good for risk assessment)
- **Confidence Level**: 95% means there's a 95% chance the price falls within the range

---

### 5. Batch Multi-Stock Predictions

**Best for**: Portfolio analysis and comparing multiple stocks simultaneously

**API**:
```bash
POST /models/predict-batch
{
  "tickers": ["AAPL", "MSFT", "GOOGL", "TSLA"],
  "model_name": "lstm",
  "days_ahead": 7
}
```

Response:
```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL", "TSLA"],
  "model_name": "lstm",
  "days_ahead": 7,
  "predictions": {
    "AAPL": {"success": true, "prediction": 150.25, "days_ahead": 7},
    "MSFT": {"success": true, "prediction": 428.75, "days_ahead": 7},
    "GOOGL": {"success": true, "prediction": 155.30, "days_ahead": 7},
    "TSLA": {"success": true, "prediction": 245.60, "days_ahead": 7}
  }
}
```

**Python**:
```python
from app.services.prediction_service import PredictionService

results = PredictionService.predict_multiple_stocks(
    ["AAPL", "MSFT", "GOOGL"],
    model_name="lstm",
    days_ahead=7
)
```

---

## Frontend Usage

### Single Stock Tab
```
1. Enter ticker symbol (e.g., AAPL)
2. Select ML model
3. Click "Train Model"
4. View performance metrics (RMSE, MAE, R², MAPE)
5. Click "Make Prediction"
6. View predicted prices
```

### Multiple Stocks Tab
```
1. Enter comma-separated tickers (e.g., AAPL,MSFT,GOOGL)
2. Select model and days ahead
3. Click "Predict Multiple Stocks"
4. View comparison table with all predictions
```

### Ensemble Tab
```
1. Enter a single ticker
2. Click "Make Ensemble Prediction"
3. View ensemble result and individual model predictions
4. See confidence range and uncertainty measures
```

### Forecast Tab
```
1. Enter ticker and select model
2. Set forecast horizon (7-90 days)
3. Click "Generate Forecast"
4. View interactive chart with confidence bands
5. Download detailed forecast table
```

---

## Model Comparison

| Model | Speed | Accuracy | Best For |
|-------|-------|----------|----------|
| Linear | Very Fast | Medium | Baseline, trending markets |
| Random Forest | Fast | High | Non-linear patterns |
| XGBoost | Medium | Very High | Complex patterns |
| LSTM | Slower | Very High | Time-series, LSTM trends |
| Ensemble | Medium | Highest | Risk-sensitive decisions |

---

## Tips for Better Predictions

### 1. Use Ensemble for Important Decisions
- Multiple models reduce single-model bias
- Standard deviation indicates confidence level
- Better for portfolio decisions

### 2. Check Confidence Intervals
- Wide intervals = more uncertainty
- Narrow intervals = more confidence
- Adjust trading strategy accordingly

### 3. Consider Time Horizon
- Shorter forecasts (7 days) are more reliable
- Longer forecasts (30+ days) have wider confidence bands
- Use for trend identification, not exact prices

### 4. Train on Sufficient Data
- Requires at least 30 days of historical data
- LSTM models need 60 days for optimal performance
- More data = better training = better predictions

### 5. Retrain Models Regularly
- Market conditions change
- Retrain models weekly or monthly
- Use the "Train Model" button in the frontend

### 6. Diversify Models
- Don't rely on one model
- Use ensemble to combine strengths
- Compare results across different models

---

## Error Handling

### Not Enough Data
```
Error: "Need at least 60 days of data for LSTM prediction"
Solution: Try a different model or wait for more historical data
```

### Model Not Found
```
Error: "Model lstm for AAPL not found"
Solution: Train the model first using the "Train Model" button
```

### API Timeout
```
Error: "Request timeout"
Solution: Predictions are being computed. Try again in a moment.
```

---

## Interpretation Guide

### Prediction Price: $150.25
This is your forecasted price at the end of your selected time period.

### Confidence Range: $145.30 - $155.20
There's a 95% probability the actual price will fall within this range.

### Std Deviation: $3.42
Measures how much individual model predictions vary. 
- **Low value**: Models agree, high confidence
- **High value**: Models disagree, lower confidence

### RMSE (Root Mean Square Error): 5.23
Measures how far predictions typically deviate from actual prices.
- **Lower is better** (smaller errors)

---

## Examples

### Example 1: Planning a Stock Purchase
```
Goal: Should I buy AAPL stock?

1. Get current price: $150.00
2. Generate ensemble prediction for 7 days: $150.25
3. Check confidence range: $145.30 - $155.20
4. See standard deviation: $3.42

Interpretation: Models moderately predict slight increase.
With wide confidence range, not a strong signal. 
Consider other factors before buying.
```

### Example 2: Portfolio Risk Assessment
```
Goal: How risky is my TSLA position?

1. Generate 30-day forecast
2. Check forecast volatility (confidence bands widen)
3. Early predictions: narrow bands ($240 - $250)
4. Late predictions: wider bands ($220 - $280)

Interpretation: More uncertainty further out. 
Position becomes riskier over time.
Consider setting stop losses.
```

### Example 3: Trend Analysis
```
Goal: Is MSFT stock trending up?

1. Generate 30-day forecast with sequential prediction
2. Plot the entire forecast line
3. Observe upward trend in predictions

Interpretation: Models see bullish trend.
But check confidence intervals - if very wide,
weak signal. Strong uptrend if narrow intervals too.
```

---

## API Documentation

Full API documentation available at: `http://localhost:8000/docs` (when running locally)

---

## Support & Contributing

For issues or feature requests:
1. Check this guide first
2. Review API documentation
3. Create an issue with details
4. Contributing guide in main README

---

## Version History

- **v1.0.0**: Initial prediction system with 4 ML models
- **v1.1.0**: Added ensemble predictions and confidence intervals
- **v1.2.0** (Latest): Added multi-day forecasting and batch predictions

---

*Last Updated: April 2024*
