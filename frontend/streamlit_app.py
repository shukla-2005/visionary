import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime

# Configuration — FASTAPI_URL is set via env var on Render
API_BASE_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")
if not API_BASE_URL.startswith(("http://", "https://")):
    API_BASE_URL = f"https://{API_BASE_URL}"

# Page configuration
st.set_page_config(
    page_title="Stock Market Analysis & Prediction",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.25rem solid #1f77b4;
    }
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Authentication functions
def login_user(username, password):
    try:
        response = requests.post(f"{API_BASE_URL}/auth/login", json={"username": username, "password": password})
        if response.status_code == 200:
            return response.json()
        return response
    except:
        return None

def register_user(username, email, password):
    try:
        response = requests.post(f"{API_BASE_URL}/auth/register", json={
            "username": username,
            "email": email,
            "password": password
        })
        return response
    except:
        return None

# Session state management
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'token' not in st.session_state:
    st.session_state.token = None
if 'username' not in st.session_state:
    st.session_state.username = None

# Sidebar navigation
def sidebar():
    st.sidebar.markdown('<div class="sidebar-header">📊 Stock Analysis</div>', unsafe_allow_html=True)

    if not st.session_state.authenticated:
        with st.sidebar:
            st.subheader("Authentication")

            tab1, tab2 = st.tabs(["Login", "Register"])

            with tab1:
                username = st.text_input("Username", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                if st.button("Login"):
                    result = login_user(username, password)
                    if isinstance(result, dict) and "access_token" in result:
                        st.session_state.authenticated = True
                        st.session_state.token = result["access_token"]
                        st.session_state.username = username
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        error_msg = "Login failed"
                        if hasattr(result, 'json'):
                            try:
                                error_detail = result.json().get("detail", "Invalid credentials")
                                error_msg += f": {error_detail}"
                            except:
                                pass
                        st.error(error_msg)

            with tab2:
                reg_username = st.text_input("Username", key="reg_username")
                reg_email = st.text_input("Email", key="reg_email")
                reg_password = st.text_input("Password", type="password", key="reg_password")
                if st.button("Register"):
                    response = register_user(reg_username, reg_email, reg_password)
                    if response and response.status_code == 200:
                        st.success("Registration successful! Please login.")
                    else:
                        error_msg = "Registration failed"
                        if response:
                            try:
                                error_detail = response.json().get("detail", "Unknown error")
                                error_msg += f": {error_detail}"
                            except:
                                pass
                        st.error(error_msg)

    else:
        st.sidebar.write(f"Welcome, {st.session_state.username}!")

        page = st.sidebar.radio("Navigation", [
            "Home Dashboard",
            "Single Stock Analysis",
            "Multi-Company Comparison",
            "Prediction",
            "History",
            "Reports",
            "Sector Analysis",
            "Stock Screener"
        ])

        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.token = None
            st.session_state.username = None
            st.rerun()

        return page

    return None

# Main content
def main():
    page = sidebar()

    if not st.session_state.authenticated and page:
        st.warning("Please login to access the application.")
        return

    if page == "Home Dashboard":
        show_home_dashboard()
    elif page == "Single Stock Analysis":
        show_single_stock_analysis()
    elif page == "Multi-Company Comparison":
        show_comparison()
    elif page == "Prediction":
        show_prediction()
    elif page == "History":
        show_history()
    elif page == "Reports":
        show_reports()
    elif page == "Sector Analysis":
        show_sector_analysis()
    elif page == "Stock Screener":
        show_stock_screener()
    else:
        show_welcome()

def show_welcome():
    st.markdown('<div class="main-header">📈 Stock Market Analysis & Prediction System</div>', unsafe_allow_html=True)

    st.markdown("""
    ## Welcome to the Advanced Stock Analysis Platform

    This comprehensive system provides:

    - **Real-time Stock Analysis**: Historical data, technical indicators, and market trends
    - **Machine Learning Predictions**: Linear Regression, Random Forest, XGBoost, and LSTM models
    - **Comparative Analysis**: Side-by-side comparison of multiple stocks
    - **Interactive Visualizations**: Plotly charts for better insights
    - **Report Generation**: Download analysis reports in CSV/PDF format

    ### Coverage
    - **US Markets**: All NYSE, NASDAQ, and AMEX listed stocks (thousands of tickers)
    - **International**: ADRs and globally listed equities
    - **Data Source**: Alpha Vantage — live market data with yfinance as fallback

    ### Key Features
    - 📊 Technical Indicators (SMA, EMA, RSI, MACD, Bollinger Bands)
    - 🤖 ML Predictions for 7, 15, and 30 days
    - 🔎 Full ticker search — find any stock by name or symbol
    - 📋 Complete market listing — browse all active listed stocks
    - 📈 Interactive Charts and Visualizations
    - 📋 Comprehensive Reporting

    Please login or register to start analyzing stocks!
    """)

def show_home_dashboard():
    st.markdown('<div class="main-header">🏠 Home Dashboard</div>', unsafe_allow_html=True)

    # Refresh button
    if st.button("🔄 Refresh Data"):
        st.rerun()

    # Top movers
    try:
        response = requests.get(f"{API_BASE_URL}/stocks/top-movers")
        if response.status_code == 200:
            movers = response.json()

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🚀 Top 10 Gainers")
                if movers.get("gainers"):
                    for gainer in movers["gainers"]:
                        st.metric(
                            f"{gainer['ticker']} - {gainer['name'][:20]}...",
                            f"${gainer['current_price']:.2f}",
                            f"{gainer['change_percent']:.2f}%"
                        )

            with col2:
                st.subheader("📉 Top 10 Losers")
                if movers.get("losers"):
                    for loser in movers["losers"]:
                        st.metric(
                            f"{loser['ticker']} - {loser['name'][:20]}...",
                            f"${loser['current_price']:.2f}",
                            f"{loser['change_percent']:.2f}%"
                        )

            # All stocks table
            st.subheader("📊 All Major Stocks Overview")
            if movers.get("all_stocks"):
                df = pd.DataFrame(movers["all_stocks"])
                df = df.sort_values('change_percent', ascending=False)
                df['change_percent'] = df['change_percent'].round(2)
                df['current_price'] = df['current_price'].round(2)
                df = df[['ticker', 'name', 'current_price', 'change_percent']]
                df.columns = ['Ticker', 'Company', 'Price ($)', 'Change (%)']
                st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Unable to fetch market data: {e}")

def show_single_stock_analysis():
    st.markdown('<div class="main-header">📊 Single Stock Analysis</div>', unsafe_allow_html=True)

    ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TSLA, TCS)", "").upper()

    if ticker:
        try:
            # Get stock info
            response = requests.get(f"{API_BASE_URL}/stocks/search/{ticker}")
            if response.status_code == 200:
                stock_info = response.json()

                # Display stock info
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Company", stock_info["name"])
                with col2:
                    st.metric("Current Price", f"${stock_info['current_price']:.2f}")
                with col3:
                    high = stock_info.get('week_52_high')
                    st.metric("52W High", f"${high:.2f}" if high else "N/A")
                with col4:
                    low = stock_info.get('week_52_low')
                    st.metric("52W Low", f"${low:.2f}" if low else "N/A")

                # Get historical data
                hist_response = requests.get(f"{API_BASE_URL}/stocks/history/{ticker}")
                if hist_response.status_code == 200:
                    hist_data = hist_response.json()

                    # Convert to DataFrame
                    df = pd.DataFrame(hist_data)
                    df['date'] = pd.to_datetime(df['date'])

                    # Candlestick chart
                    fig = go.Figure(data=[go.Candlestick(
                        x=df['date'],
                        open=df['open'],
                        high=df['high'],
                        low=df['low'],
                        close=df['close']
                    )])

                    fig.update_layout(
                        title=f"{ticker} Candlestick Chart",
                        xaxis_title="Date",
                        yaxis_title="Price",
                        height=600
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Volume chart
                    fig_vol = go.Figure(data=[go.Bar(
                        x=df['date'],
                        y=df['volume'],
                        name="Volume"
                    )])

                    fig_vol.update_layout(
                        title=f"{ticker} Volume Chart",
                        xaxis_title="Date",
                        yaxis_title="Volume",
                        height=300
                    )

                    st.plotly_chart(fig_vol, use_container_width=True)

                # Technical indicators
                indicators_response = requests.get(f"{API_BASE_URL}/stocks/indicators/{ticker}")
                if indicators_response.status_code == 200:
                    indicators = indicators_response.json()

                    if indicators:
                        st.subheader("Technical Indicators")

                        # RSI Chart
                        df_indicators = pd.DataFrame(indicators)
                        fig_rsi = go.Figure()
                        fig_rsi.add_trace(go.Scatter(
                            y=df_indicators['rsi'].dropna(),
                            mode='lines',
                            name='RSI'
                        ))
                        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
                        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")

                        fig_rsi.update_layout(
                            title="RSI Indicator",
                            height=300
                        )

                        st.plotly_chart(fig_rsi, use_container_width=True)

            else:
                st.error(f"Stock {ticker} not found")

        except Exception as e:
            st.error(f"Error fetching data: {e}")

def show_comparison():
    st.markdown('<div class="main-header">⚖️ Multi-Company Comparison</div>', unsafe_allow_html=True)

    tickers_input = st.text_input("Enter tickers separated by commas (e.g., AAPL,MSFT,GOOGL)")
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

    if len(tickers) >= 2 and len(tickers) <= 5:
        try:
            response = requests.post(f"{API_BASE_URL}/stocks/compare", json={"tickers": tickers})
            if response.status_code == 200:
                data = response.json()

                # Create comparison chart
                fig = go.Figure()

                for ticker in tickers:
                    if ticker in data["data"]:
                        df = pd.DataFrame(data["data"][ticker])
                        df['date'] = pd.to_datetime(df['date'])

                        fig.add_trace(go.Scatter(
                            x=df['date'],
                            y=df['close'],
                            mode='lines',
                            name=ticker
                        ))

                fig.update_layout(
                    title="Stock Price Comparison",
                    xaxis_title="Date",
                    yaxis_title="Price",
                    height=600
                )

                st.plotly_chart(fig, use_container_width=True)

            else:
                st.error("Error fetching comparison data")

        except Exception as e:
            st.error(f"Error: {e}")
    elif len(tickers) > 5:
        st.warning("Please compare maximum 5 stocks at a time")

def show_prediction():
    st.markdown('<div class="main-header">🔮 Stock Price Prediction</div>', unsafe_allow_html=True)

    # Tabs for different prediction modes
    tab1, tab2, tab3, tab4 = st.tabs(["Single Stock", "Multiple Stocks", "Ensemble", "Forecast"])

    with tab1:
        st.subheader("Single Stock Prediction")
        col1, col2 = st.columns([1, 1])

        with col1:
            ticker = st.text_input("Stock Ticker", "").upper()

        with col2:
            model = st.selectbox("Model", ["linear", "rf", "xgb", "lstm"])

        days_options = st.multiselect("Prediction Days", [7, 15, 30], default=[7], key="single_days")

        if st.button("Train Model", key="train_single") and ticker:
            try:
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                response = requests.post(
                    f"{API_BASE_URL}/models/train/{ticker}",
                    json={"ticker": ticker, "models": [model]},
                    headers=headers
                )

                if response.status_code == 200:
                    result = response.json()
                    st.success(f"Model trained successfully! Best model: {result['best_model']}")

                    # Display metrics
                    if model in result.get("metrics", {}):
                        metrics = result["metrics"][model]
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.metric("RMSE", f"{metrics['rmse']:.4f}")
                        with col2:
                            st.metric("MAE", f"{metrics['mae']:.4f}")
                        with col3:
                            st.metric("R² Score", f"{metrics['r2_score']:.4f}")
                        with col4:
                            st.metric("MAPE", f"{metrics['mape']:.2f}%")
                    else:
                        st.info("Training complete. No metrics available for selected model.")
                else:
                    st.error(f"Training failed: {response.json().get('detail', 'Unknown error')}")

            except Exception as e:
                st.error(f"Error: {e}")

        if st.button("Make Prediction", key="make_single") and ticker and days_options:
            try:
                headers = {"Authorization": f"Bearer {st.session_state.token}"}

                predictions = {}
                for days in days_options:
                    response = requests.post(
                        f"{API_BASE_URL}/models/predict/{ticker}",
                        json={"ticker": ticker, "model_name": model, "days_ahead": days},
                        headers=headers
                    )

                    if response.status_code == 200:
                        pred = response.json()
                        predictions[days] = pred["predicted_price"]
                    else:
                        st.warning(f"Prediction failed for {days} days: {response.json().get('detail', 'Unknown error')}")
                        predictions[days] = None

                # Display predictions
                st.subheader("Predictions")
                cols = st.columns(len(predictions))
                for idx, (days, price) in enumerate(predictions.items()):
                    with cols[idx]:
                        if price:
                            st.metric(f"{days} Days", f"${price:.2f}")
                        else:
                            st.error(f"Failed to predict {days} days ahead")

            except Exception as e:
                st.error(f"Error: {e}")

    with tab2:
        st.subheader("Multiple Stock Predictions")
        tickers_input = st.text_area("Enter tickers (comma-separated)", "AAPL,MSFT,GOOGL")
        model_batch = st.selectbox("Model", ["linear", "rf", "xgb", "lstm"], key="batch_model")
        days_batch = st.select_slider("Days Ahead", options=list(range(1, 61)), value=7, key="batch_days")

        if st.button("Predict Multiple Stocks", key="predict_batch"):
            try:
                tickers_list = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
                headers = {"Authorization": f"Bearer {st.session_state.token}"}

                response = requests.post(
                    f"{API_BASE_URL}/models/predict-batch",
                    json={
                        "tickers": tickers_list,
                        "model_name": model_batch,
                        "days_ahead": days_batch
                    },
                    headers=headers
                )

                if response.status_code == 200:
                    result = response.json()
                    st.success(f"Predictions completed for {len(tickers_list)} stocks")

                    # Create comparison table
                    pred_data = []
                    for ticker, pred in result["predictions"].items():
                        if pred.get("success"):
                            pred_data.append({
                                "Ticker": ticker,
                                "Predicted Price": f"${pred['prediction']:.2f}",
                                "Days Ahead": pred["days_ahead"]
                            })

                    if pred_data:
                        df = pd.DataFrame(pred_data)
                        st.dataframe(df, use_container_width=True)
                else:
                    st.error("Batch prediction failed")

            except Exception as e:
                st.error(f"Error: {e}")

    with tab3:
        st.subheader("Ensemble Prediction (Multiple Models)")
        ticker_ens = st.text_input("Stock Ticker", "", key="ensemble_ticker").upper()
        days_ens = st.select_slider("Days Ahead", options=list(range(1, 61)), value=7, key="ensemble_days")

        if st.button("Make Ensemble Prediction", key="predict_ensemble"):
            try:
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                response = requests.post(
                    f"{API_BASE_URL}/models/ensemble/{ticker_ens}",
                    json={"ticker": ticker_ens, "model_name": "linear", "days_ahead": days_ens},
                    headers=headers
                )

                if response.status_code == 200:
                    result = response.json()
                    st.success(f"Ensemble Prediction for {ticker_ens}")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Ensemble Price", f"${result['ensemble_prediction']:.2f}")
                    with col2:
                        st.metric("Std Deviation", f"${result['std_deviation']:.2f}")
                    with col3:
                        st.metric("Confidence Range", f"${result['lower_bound']:.2f} - ${result['upper_bound']:.2f}")

                    # Show individual model predictions
                    st.subheader("Individual Model Predictions")
                    model_preds = []
                    for model_name, model_data in result["model_predictions"].items():
                        if "error" not in model_data:
                            model_preds.append({
                                "Model": model_name,
                                "Predicted Price": f"${model_data['price']:.2f}"
                            })
                    if model_preds:
                        df = pd.DataFrame(model_preds)
                        st.dataframe(df, use_container_width=True)

                else:
                    st.error("Ensemble prediction failed")

            except Exception as e:
                st.error(f"Error: {e}")

    with tab4:
        st.subheader("Future Price Forecast")
        ticker_forecast = st.text_input("Stock Ticker", "", key="forecast_ticker").upper()
        model_forecast = st.selectbox("Model", ["linear", "rf", "xgb", "lstm"], key="forecast_model")
        days_forecast = st.slider("Forecast Days", 7, 90, 30, key="forecast_days")

        if st.button("Generate Forecast", key="generate_forecast"):
            try:
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                response = requests.post(
                    f"{API_BASE_URL}/models/forecast/{ticker_forecast}?days={days_forecast}",
                    json={"ticker": ticker_forecast, "model_name": model_forecast, "days_ahead": days_forecast},
                    headers=headers
                )

                if response.status_code == 200:
                    result = response.json()
                    st.success(f"Forecast generated for {ticker_forecast}")

                    # Create forecast dataframe
                    forecast_df = pd.DataFrame(result["forecast"])
                    forecast_df['date'] = pd.to_datetime(forecast_df['date'])

                    # Create interactive chart
                    import plotly.graph_objects as go
                    fig = go.Figure()

                    fig.add_trace(go.Scatter(
                        x=forecast_df['date'],
                        y=forecast_df['predicted_price'],
                        mode='lines+markers',
                        name='Predicted Price',
                        line=dict(color='blue', width=2)
                    ))

                    fig.add_trace(go.Scatter(
                        x=forecast_df['date'],
                        y=forecast_df['upper_bound'],
                        fill=None,
                        mode='lines',
                        line_color='rgba(0,100,200,0)',
                        showlegend=False
                    ))

                    fig.add_trace(go.Scatter(
                        x=forecast_df['date'],
                        y=forecast_df['lower_bound'],
                        fill='tonexty',
                        mode='lines',
                        line_color='rgba(0,100,200,0)',
                        name='Confidence Interval',
                        fillcolor='rgba(0,100,200,0.2)'
                    ))

                    fig.update_layout(
                        title=f'{ticker_forecast} Price Forecast',
                        xaxis_title='Date',
                        yaxis_title='Price ($)',
                        hovermode='x unified',
                        height=500
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Display forecast table
                    st.subheader("Forecast Details")
                    forecast_display = forecast_df[['date', 'predicted_price', 'lower_bound', 'upper_bound', 'confidence']].copy()
                    forecast_display['date'] = forecast_display['date'].dt.strftime('%Y-%m-%d')
                    st.dataframe(forecast_display, use_container_width=True)

                else:
                    st.error("Forecast generation failed")

            except Exception as e:
                st.error(f"Error: {e}")

def show_history():
    st.markdown('<div class="main-header">📋 Prediction History</div>', unsafe_allow_html=True)

    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(f"{API_BASE_URL}/history", headers=headers)

        if response.status_code == 200:
            history = response.json()

            if history:
                df = pd.DataFrame(history)
                if 'created_at' in df.columns:
                    df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
                display_cols = [c for c in ['ticker', 'model_name', 'predicted_price', 'days_ahead', 'created_at'] if c in df.columns]
                st.dataframe(df[display_cols], use_container_width=True)
            else:
                st.info("No prediction history found")

        else:
            st.error("Failed to fetch history")

    except Exception as e:
        st.error(f"Error: {e}")

def show_reports():
    st.markdown('<div class="main-header">📄 Reports & Downloads</div>', unsafe_allow_html=True)

    ticker = st.text_input("Stock Ticker for Report", "").upper()
    format_type = st.selectbox("Format", ["csv", "pdf"])

    if st.button("Generate Report") and ticker:
        try:
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            response = requests.get(
                f"{API_BASE_URL}/report/{ticker}?format={format_type}",
                headers=headers
            )

            if response.status_code == 200:
                # Download file
                st.download_button(
                    label=f"Download {ticker} Report",
                    data=response.content,
                    file_name=f"{ticker}_report.{format_type}",
                    mime="application/octet-stream"
                )
            else:
                st.error("Report generation failed")

        except Exception as e:
            st.error(f"Error: {e}")

def show_sector_analysis():
    st.markdown('<div class="main-header">🏢 Sector Analysis</div>', unsafe_allow_html=True)

    try:
        response = requests.get(f"{API_BASE_URL}/stocks/sector-analysis")
        if response.status_code == 200:
            sectors = response.json()

            for sector_data in sectors:
                with st.expander(f"{sector_data['sector']} Sector"):
                    st.metric("Average Performance", f"{sector_data['average_performance']:.2f}%")

                    # Display stocks in sector
                    stocks_df = pd.DataFrame(sector_data['stocks'])
                    available_cols = [c for c in ['ticker', 'name', 'current_price'] if c in stocks_df.columns]
                    st.dataframe(stocks_df[available_cols])

        else:
            st.error("Failed to fetch sector data")

    except Exception as e:
        st.error(f"Error: {e}")

def show_stock_screener():
    st.markdown('<div class="main-header">🔍 Stock Screener</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Search by Name / Symbol", "Browse All Listed Stocks"])

    with tab1:
        st.subheader("Find a Stock")
        query = st.text_input("Enter company name or ticker (e.g. 'Apple', 'TSLA', 'Microsoft')", "")
        if query:
            try:
                resp = requests.get(f"{API_BASE_URL}/stocks/ticker-search", params={"q": query})
                if resp.status_code == 200:
                    data = resp.json()
                    results = data.get("results", [])
                    if results:
                        df = pd.DataFrame(results)
                        df.columns = [c.capitalize() for c in df.columns]
                        st.dataframe(df, use_container_width=True)
                        st.caption(f"{len(results)} result(s) found")
                    else:
                        st.info("No matches found. Try a different name or symbol.")
                else:
                    st.error("Search failed. Please try again.")
            except Exception as e:
                st.error(f"Error: {e}")

    with tab2:
        st.subheader("All Active Listed Stocks")
        st.info("Loads the full list of stocks listed on NYSE, NASDAQ, and AMEX from Alpha Vantage.")

        if st.button("Load Full Listing"):
            with st.spinner("Fetching full market listing..."):
                try:
                    resp = requests.get(f"{API_BASE_URL}/stocks/listed", params={"state": "active"})
                    if resp.status_code == 200:
                        data = resp.json()
                        stocks = data.get("stocks", [])
                        if stocks:
                            df = pd.DataFrame(stocks)
                            st.success(f"Loaded {data.get('count', len(stocks))} listed stocks")

                            # Filters
                            col1, col2 = st.columns(2)
                            with col1:
                                exchanges = ["All"] + sorted(df["exchange"].dropna().unique().tolist()) if "exchange" in df.columns else ["All"]
                                selected_exchange = st.selectbox("Filter by Exchange", exchanges)
                            with col2:
                                asset_types = ["All"] + sorted(df["assetType"].dropna().unique().tolist()) if "assetType" in df.columns else ["All"]
                                selected_type = st.selectbox("Filter by Asset Type", asset_types)

                            filtered = df.copy()
                            if selected_exchange != "All" and "exchange" in filtered.columns:
                                filtered = filtered[filtered["exchange"] == selected_exchange]
                            if selected_type != "All" and "assetType" in filtered.columns:
                                filtered = filtered[filtered["assetType"] == selected_type]

                            st.dataframe(filtered, use_container_width=True)
                            st.caption(f"Showing {len(filtered)} of {len(df)} stocks")
                        else:
                            st.warning("No stocks returned.")
                    else:
                        st.error("Failed to fetch listing.")
                except Exception as e:
                    st.error(f"Error: {e}")

if __name__ == "__main__":
    main()