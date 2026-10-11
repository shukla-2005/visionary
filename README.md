# Stock Market Analysis & Prediction

A full-stack application for exploring historical stock data, comparing companies, and generating machine-learning forecasts. The project combines a Streamlit dashboard with a FastAPI backend and a relational database for user accounts and prediction history.

## Overview

Users can look up stocks, review price history and technical indicators, compare companies, and request single-stock or multi-day predictions. The application also supports saved prediction history and downloadable stock reports.

This project is for analysis and education. Forecasts are model estimates, not financial advice or guarantees of future performance.

## Data

The application retrieves market information on demand:

- **Historical prices for analysis and model training:** Yahoo Finance through `yfinance`.
- **Ticker search and US listing information:** Alpha Vantage endpoints; these features require an Alpha Vantage API key.
- **Price and volume fields:** date, open, high, low, close, and volume.
- **Derived features:** returns, rolling volatility and statistics, price ranges, lagged values, volume trends, and calendar features.

Data availability depends on the upstream providers and their rate limits. No private or static market dataset is required to get started.

## Project Workflow

1. **Retrieve market data** for a requested ticker and time period.
2. **Prepare and engineer features** from prices, volume, and dates; scale the model inputs.
3. **Train or load forecasting models** such as Linear Regression, Random Forest, XGBoost, and (where TensorFlow is installed) LSTM.
4. **Generate predictions** for one or more tickers, including ensemble estimates, multi-day forecasts, and confidence ranges.
5. **Explore the results** in the Streamlit dashboard or through the FastAPI endpoints.
6. **Save prediction history** for authenticated users and download CSV or PDF stock reports.

## Dashboard

The Streamlit app includes:

- Home dashboard with market movers
- Single-stock analysis and historical charts
- Multi-company comparison
- Model training, individual predictions, ensemble estimates, and forecasts
- Prediction history
- CSV/PDF report downloads
- Sector analysis and a stock screener
- Account registration and login

## Results

The application returns stock prices, technical-analysis data, model predictions, forecast timelines, and generated reports. Prediction quality depends on the ticker, available history, selected model, and market conditions. Model metrics are produced during training; no fixed accuracy or investment-return claim is made here.

## Technology

- **UI:** Streamlit
- **API:** FastAPI, Uvicorn
- **Data and analysis:** Python, pandas, NumPy, yfinance
- **Machine learning:** scikit-learn, XGBoost, TensorFlow/Keras (optional for LSTM)
- **Charts:** Plotly
- **Persistence:** SQLAlchemy with SQLite locally or PostgreSQL in deployment
- **Deployment:** Docker Compose or Render Blueprint

## How to Run

### Prerequisites

- Python 3.10 (recommended; the Render Blueprint uses Python 3.10)
- Git
- An Alpha Vantage API key if you need ticker search or US listing features

### Run locally with Python

1. Clone the repository and enter its directory:

   ```bash
   git clone https://github.com/shukla-2005/visionary.git
   cd visionary
   ```

2. Create and activate a virtual environment.

   **Windows PowerShell:**

   ```powershell
   py -3.10 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS/Linux:**

   ```bash
   python3.10 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Create a local environment file and set your own values:

   **Windows PowerShell:**

   ```powershell
   Copy-Item .env.example .env
   ```

   **macOS/Linux:**

   ```bash
   cp .env.example .env
   ```

   Set a unique local `SECRET_KEY`. Add `ALPHA_VANTAGE_API_KEY` if using Alpha Vantage-backed lookup features. Do not commit `.env`.

5. Start the API in the first terminal:

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. Start the dashboard in a second terminal:

   **Windows PowerShell** (use the local API started above):

   ```powershell
   $env:FASTAPI_URL = "http://localhost:8000"
   streamlit run frontend/streamlit_app.py --server.port 8501
   ```

   **macOS/Linux:**

   ```bash
   export FASTAPI_URL="http://localhost:8000"
   streamlit run frontend/streamlit_app.py --server.port 8501
   ```

7. Open:

   - Dashboard: <http://localhost:8501>
   - API health check: <http://localhost:8000/health>
   - Interactive API documentation: <http://localhost:8000/docs>

The database tables are created automatically when the API starts. For local use, SQLite is the default.

### Run with Docker Compose

With Docker Desktop running, from the repository root run:

```bash
docker compose up --build
```

Open the dashboard at <http://localhost:8501> and API docs at <http://localhost:8000/docs>. To stop the services, press `Ctrl+C` and run `docker compose down`.

## API

FastAPI provides interactive endpoint documentation at `/docs`. Main endpoint groups include:

- `/auth` — registration and login
- `/stocks` — stock lookup, price history, indicators, comparison, sector analysis, and market movers
- `/models` — training, prediction, ensemble, confidence, forecast, and batch prediction
- `/history` — authenticated prediction history
- `/report` — authenticated CSV/PDF report generation

Prediction, history, and report operations require authentication. Use the interactive API docs to inspect request schemas and try endpoints.

## Deployment

The deployed FastAPI backend is available at <https://stock-analysis-api-0dqg.onrender.com>.

- Health check: <https://stock-analysis-api-0dqg.onrender.com/health>
- Interactive API documentation: <https://stock-analysis-api-0dqg.onrender.com/docs>

The Streamlit frontend is configured to use this backend by default. To connect a
different backend, set `FASTAPI_URL` to its base URL. The Render Blueprint
(`render.yaml`) automatically wires the frontend service to the API service.
See [deployment_instructions.md](deployment_instructions.md) for setup steps and
production notes.

## Repository Layout

```text
app/                  FastAPI routes, services, database, schemas, and auth
frontend/              Streamlit dashboard
ml/                    Data loading, feature engineering, training, and prediction
saved_models/          Included trained model artifacts
tests/                 API tests and database utilities
reports/               Sample/generated reports
render.yaml            Render Blueprint
docker-compose.yml     Local container setup
requirements.txt       Full local dependencies, including TensorFlow
requirements-render.txt Dependencies used by the Render services
```
