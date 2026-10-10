# Stock Market Analysis and Prediction System

A comprehensive full-stack web application for analyzing and predicting stock prices of various listed companies using machine learning.

## Features

- **Stock Analysis**: Historical data, technical indicators, volatility analysis
- **Comparative Analysis**: Compare multiple stocks side by side
- **🆕 Advanced Machine Learning Predictions**:
  - Individual model predictions (Linear Regression, Random Forest, XGBoost, LSTM)
  - **Ensemble predictions** combining multiple models
  - **Multi-day forecasting** with sequential predictions
  - **Confidence intervals** with volatility-based uncertainty estimates
  - **Batch predictions** for multiple stocks at once
  - **Future price forecasts** with visualization and date ranges
- **User Authentication**: JWT-based login/signup
- **Interactive Dashboard**: Streamlit frontend with Plotly visualizations
- **Report Generation**: Download analysis reports in CSV/PDF
- **Stock Screener**: Filter stocks by various criteria
- **Sector Analysis**: Analyze stocks by sector
- **Prediction History**: Track and review all historical predictions

## Tech Stack

- **Backend**: FastAPI, Python
- **Frontend**: Streamlit
- **Database**: SQLite (default), PostgreSQL (production)
- **ML**: scikit-learn, XGBoost, TensorFlow/Keras
- **Data**: yfinance, pandas, numpy
- **Visualization**: Plotly, matplotlib
- **Deployment**: Docker

## Project Structure

```
visionary/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── auth.py
│   │   ├── stocks.py
│   │   ├── models.py (Enhanced with prediction endpoints)
│   │   ├── history.py
│   │   └── reports.py
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   │   └── prediction_service.py (Enhanced with ensemble/forecast methods)
│   └── utils/
├── frontend/
│   ├── streamlit_app.py (Enhanced prediction UI with tabs)
│   └── pages/
├── ml/
│   ├── predict.py (Enhanced with sequential forecasting)
│   ├── train.py
│   ├── lstm_model.py
│   └── ...
├── reports/
├── saved_models/
├── tests/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd visionary
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Run the FastAPI backend**
   ```bash
   uvicorn app.main:app --reload
   ```

7. **Run the Streamlit frontend** (in another terminal)
   ```bash
   streamlit run frontend/streamlit_app.py
   ```

## Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Access the application**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## API Endpoints

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /stocks/search/{ticker}` - Search stock by ticker
- `GET /stocks/history/{ticker}` - Get historical data
- `GET /stocks/indicators/{ticker}` - Get technical indicators
- `POST /stocks/compare` - Compare multiple stocks
- `GET /stocks/sector-analysis` - Sector analysis
- `GET /stocks/top-movers` - Top gainers/losers
- `POST /models/train/{ticker}` - Train ML models
- `GET /models/compare/{ticker}` - Compare model performance
- `POST /predict/{ticker}` - Make predictions
- `GET /history` - User prediction history
- `GET /report/{ticker}` - Generate report

## Advanced Prediction Features

### 1. Ensemble Predictions
Combine predictions from multiple ML models for more robust forecasts:
- Averages predictions from Linear Regression, Random Forest, XGBoost, and LSTM
- Provides standard deviation for uncertainty estimation
- Confidence range based on model disagreement

**API Endpoint**: `POST /models/ensemble/{ticker}`

### 2. Future Price Forecasts
Generate sequential, multi-day price forecasts with visualization:
- Recursive predictions for 7-90 days
- Confidence intervals that widen with time horizon
- Interactive Plotly charts showing forecast trends
- Date-stamped predictions for easy tracking

**API Endpoint**: `POST /models/forecast/{ticker}?days={num_days}`

### 3. Confidence Intervals
Get uncertainty estimates for predictions:
- Volatility-based confidence calculations
- Historical data used to compute realistic ranges
- Confidence levels that adapt to prediction horizon

**API Endpoint**: `POST /models/confidence/{ticker}`

### 4. Batch Predictions
Predict prices for multiple stocks simultaneously:
- Efficient batch processing
- Useful for portfolio analysis
- Automatic history tracking for each prediction

**API Endpoint**: `POST /models/predict-batch`
```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL"],
  "model_name": "lstm",
  "days_ahead": 7
}
```

### 5. Multi-Day Sequential Forecasting
Recursive predictions that use previous day's forecast as input:
- More realistic multi-day trends
- Better captures market momentum
- Works with all model types

**Python Function**: `predict_future_sequence(ticker, model_name, num_days)`

## Frontend Prediction Dashboard

The Streamlit frontend provides 4 prediction modes:

### Single Stock Prediction
- Train individual models
- Make predictions for specific time horizons
- View detailed metrics

### Multiple Stock Predictions
- Compare predictions across multiple stocks
- Batch processing for efficiency
- Side-by-side comparison tables

### Ensemble Predictions
- Leverage multiple models
- See individual model contributions
- Confidence ranges from model disagreement

### Future Price Forecasts
- Visual trendlines with confidence bands
- Interactive Plotly charts
- Detailed forecast tables with dates

## Usage

1. **Sign up/Login** to access the dashboard
2. **Search for stocks** using ticker symbols (e.g., AAPL, TSLA)
3. **Analyze historical data** and technical indicators
4. **Compare multiple stocks** side by side
5. **Train ML models** and make price predictions
6. **Use advanced features**:
   - Generate ensemble predictions for better accuracy
   - Create future forecasts with visualization
   - Batch predict multiple stocks
   - Download reports in CSV or PDF format

## Deployment

### Streamlit Cloud
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Set environment variables
4. Deploy

### Railway/Render
1. Use the Dockerfile
2. Set environment variables
3. Deploy the container

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Submit a pull request

## License

MIT License