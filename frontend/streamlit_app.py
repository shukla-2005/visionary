import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import os
from datetime import datetime

# Render free instances can take over 50 seconds to wake after inactivity.
REQUEST_TIMEOUT = 90

# Page configuration
st.set_page_config(
    page_title="Stock Market Analysis & Prediction",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Prefer environment variables for Render/local runs and Streamlit secrets on
# Community Cloud.
try:
    configured_api_url = os.getenv("FASTAPI_URL") or st.secrets.get("FASTAPI_URL")
except FileNotFoundError:
    configured_api_url = os.getenv("FASTAPI_URL")

API_BASE_URL = (
    configured_api_url or "https://stock-analysis-api-0dqg.onrender.com"
).strip().rstrip("/")
if not API_BASE_URL.startswith(("http://", "https://")):
    API_BASE_URL = f"https://{API_BASE_URL}"

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: bold;
        color: #4f8bf9;
        margin: 0.4rem 0 0.6rem;
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
    [data-testid="stMetric"] {
        border: 1px solid rgba(128, 128, 128, 0.18);
        border-radius: 0.7rem;
        padding: 0.8rem 1rem;
        background: rgba(128, 128, 128, 0.04);
    }
    div.stButton > button, div.stFormSubmitButton > button {
        border-radius: 0.55rem;
        transition: transform 120ms ease, box-shadow 120ms ease;
    }
    div.stButton > button:hover, div.stFormSubmitButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(79, 139, 249, 0.18);
    }
</style>
""", unsafe_allow_html=True)

def api_request(method, path, *, authenticated=False, **kwargs):
    headers = dict(kwargs.pop("headers", {}))
    if authenticated and st.session_state.get("token"):
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    return requests.request(
        method,
        f"{API_BASE_URL}{path}",
        headers=headers,
        timeout=REQUEST_TIMEOUT,
        **kwargs,
    )

def show_api_error(action, response=None, error=None):
    if error is not None:
        st.error(f"{action} failed: {error}")
    elif response is not None:
        st.error(f"{action} failed: {api_error_detail(response)}")

def page_header(title, description):
    st.markdown(f'<div class="main-header">{title}</div>', unsafe_allow_html=True)
    st.caption(description)

def open_stock_analysis(ticker):
    st.session_state["analysis_ticker_input"] = ticker
    st.session_state["app_navigation"] = "Single Stock Analysis"

# Authentication functions
def login_user(username, password):
    try:
        response = api_request(
            "POST", "/auth/login",
            json={"username": username, "password": password},
        )
        if response.status_code == 200:
            return response.json()
        return response
    except requests.RequestException as error:
        return error

def register_user(username, email, password):
    return api_request(
        "POST",
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password
        },
    )

def api_error_detail(response):
    try:
        payload = response.json()
    except ValueError:
        return response.text.strip() or "The server returned an empty error response."

    detail = payload.get("detail", "The request could not be completed.")
    if isinstance(detail, list):
        messages = []
        for error in detail:
            location = error.get("loc", [])
            field = ".".join(str(part) for part in location if part != "body")
            message = error.get("msg", "Invalid value")
            messages.append(f"{field}: {message}" if field else message)
        return "; ".join(messages)
    return str(detail)

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
                with st.form("login_form"):
                    username = st.text_input("Username", key="login_username")
                    password = st.text_input(
                        "Password", type="password", key="login_password"
                    )
                    login_submitted = st.form_submit_button(
                        "Login", type="primary", use_container_width=True
                    )
                if login_submitted:
                    result = login_user(username, password)
                    if isinstance(result, dict) and "access_token" in result:
                        st.session_state.authenticated = True
                        st.session_state.token = result["access_token"]
                        st.session_state.username = username
                        st.success("Logged in successfully!")
                        st.rerun()
                    elif isinstance(result, requests.RequestException):
                        st.error(
                            f"Could not reach the API at {API_BASE_URL}. "
                            f"Check that the backend is running. ({result})"
                        )
                    else:
                        show_api_error("Login", response=result)

            with tab2:
                with st.form("registration_form"):
                    reg_username = st.text_input("Username", key="reg_username")
                    reg_email = st.text_input("Email", key="reg_email")
                    reg_password = st.text_input(
                        "Password", type="password", key="reg_password"
                    )
                    registration_submitted = st.form_submit_button("Register")

                if registration_submitted:
                    reg_username = reg_username.strip()
                    reg_email = reg_email.strip()
                    if not reg_username or not reg_email or not reg_password:
                        st.error("Enter a username, email address, and password.")
                    else:
                        try:
                            response = register_user(
                                reg_username, reg_email, reg_password
                            )
                        except requests.RequestException as error:
                            st.error(
                                "Could not reach the registration service. "
                                f"Check that the FastAPI backend is running at "
                                f"{API_BASE_URL}. ({error})"
                            )
                        else:
                            if response.status_code == 200:
                                st.success(
                                    "Registration successful! Select the Login tab "
                                    "to sign in."
                                )
                            else:
                                st.error(
                                    f"Registration failed: "
                                    f"{api_error_detail(response)}"
                                )

    else:
        st.sidebar.write(f"Welcome, {st.session_state.username}!")
        st.sidebar.caption("Choose a workspace")

        page = st.sidebar.radio("Navigation", [
            "Home Dashboard",
            "Single Stock Analysis",
            "Multi-Company Comparison",
            "Prediction",
            "History",
            "Reports",
            "Sector Analysis",
            "Stock Screener"
        ], key="app_navigation")

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
    st.markdown(
        '<div class="main-header">📈 Explore the stock market</div>',
        unsafe_allow_html=True,
    )
    st.write(
        "Look up a company, explore its recent price history, and compare market "
        "movers. Sign in or register in the sidebar to access predictions, reports, "
        "and your saved analysis."
    )

    st.markdown("### Start with a popular ticker")
    popular_tickers = st.columns(5)
    for column, ticker in zip(popular_tickers, ["AAPL", "MSFT", "NVDA", "TSLA", "GOOGL"]):
        with column:
            if st.button(ticker, key=f"welcome_ticker_{ticker}", use_container_width=True):
                st.session_state["welcome_ticker_input"] = ticker
                st.rerun()

    with st.form("welcome_stock_lookup"):
        ticker_column, period_column, submit_column = st.columns([2, 1, 1])
        with ticker_column:
            ticker = st.text_input(
                "Company ticker",
                value=st.session_state.get("welcome_ticker_input", "AAPL"),
                key="welcome_ticker_input",
                placeholder="For example, AAPL",
            ).strip().upper()
        with period_column:
            period = st.selectbox(
                "History",
                ["1mo", "3mo", "6mo", "1y", "5y"],
                index=3,
                key="welcome_history_period",
            )
        with submit_column:
            st.write("")
            st.write("")
            search_submitted = st.form_submit_button(
                "Explore stock", type="primary", use_container_width=True
            )

    if search_submitted:
        if not ticker:
            st.warning("Enter a ticker symbol to explore.")
        else:
            try:
                with st.spinner(f"Loading {ticker} market data..."):
                    info_response = api_request("GET", f"/stocks/search/{ticker}")
                    info_response.raise_for_status()
                    stock_info = info_response.json()

                    history_response = api_request(
                        "GET",
                        f"/stocks/history/{ticker}",
                        params={"period": period},
                    )
                    history_response.raise_for_status()
                    history = history_response.json()

                if not history:
                    st.info(f"No price history is currently available for {ticker}.")
                else:
                    prices = pd.DataFrame(history)
                    prices["date"] = pd.to_datetime(prices["date"])
                    prices = prices.sort_values("date")
                    latest_close = float(prices["close"].iloc[-1])
                    first_close = float(prices["close"].iloc[0])
                    period_change = (
                        (latest_close / first_close - 1) * 100 if first_close else 0
                    )

                    st.subheader(
                        f"{stock_info.get('name', ticker)} ({stock_info.get('ticker', ticker)})"
                    )
                    price_column, change_column, high_column, low_column = st.columns(4)
                    price_column.metric("Latest close", f"${latest_close:,.2f}")
                    change_column.metric(
                        f"Change over {period}",
                        f"{period_change:+.2f}%",
                    )
                    high = stock_info.get("week_52_high")
                    low = stock_info.get("week_52_low")
                    high_column.metric(
                        "52-week high", f"${high:,.2f}" if high is not None else "N/A"
                    )
                    low_column.metric(
                        "52-week low", f"${low:,.2f}" if low is not None else "N/A"
                    )

                    prices["SMA 20"] = prices["close"].rolling(20).mean()
                    figure = go.Figure()
                    figure.add_trace(
                        go.Scatter(
                            x=prices["date"],
                            y=prices["close"],
                            mode="lines",
                            name="Close",
                            line={"color": "#4F8BF9", "width": 2},
                        )
                    )
                    if prices["SMA 20"].notna().any():
                        figure.add_trace(
                            go.Scatter(
                                x=prices["date"],
                                y=prices["SMA 20"],
                                mode="lines",
                                name="20-day average",
                                line={"color": "#F4A261", "width": 1.5},
                            )
                        )
                    figure.update_layout(
                        title=f"{ticker} price history",
                        xaxis_title="Date",
                        yaxis_title="Price (USD)",
                        hovermode="x unified",
                        height=420,
                        margin={"t": 55, "b": 20, "l": 10, "r": 10},
                        legend={"orientation": "h", "y": 1.12},
                    )
                    figure.update_xaxes(rangeslider_visible=True)
                    st.plotly_chart(figure, use_container_width=True)
            except requests.RequestException as error:
                response = getattr(error, "response", None)
                detail = ""
                if response is not None:
                    try:
                        detail = response.json().get("detail", "")
                    except ValueError:
                        detail = response.text
                st.error(
                    f"Could not load {ticker} market data."
                    + (f" {detail}" if detail else f" {error}")
                )
            except (KeyError, TypeError, ValueError) as error:
                st.error(f"Received unexpected market data for {ticker}: {error}")

    st.divider()
    st.subheader("Today's market movers")
    st.caption("Load the latest available market overview from the data provider.")
    if st.button("Load market movers", key="welcome_load_movers"):
        try:
            with st.spinner("Loading market movers..."):
                movers_response = api_request("GET", "/stocks/top-movers")
                movers_response.raise_for_status()
                st.session_state["welcome_market_movers"] = movers_response.json()
        except requests.RequestException as error:
            st.error(f"Could not load market movers: {error}")

    movers = st.session_state.get("welcome_market_movers")
    if movers:
        gainers_column, losers_column = st.columns(2)
        for column, label, key in [
            (gainers_column, "Top gainers", "gainers"),
            (losers_column, "Top decliners", "losers"),
        ]:
            with column:
                st.markdown(f"**{label}**")
                rows = movers.get(key, [])
                if rows:
                    table = pd.DataFrame(rows)
                    visible_columns = [
                        name for name in ["ticker", "name", "current_price", "change_percent"]
                        if name in table.columns
                    ]
                    st.dataframe(
                        table[visible_columns].head(5),
                        hide_index=True,
                        use_container_width=True,
                    )
                else:
                    st.info("No market mover data is available right now.")

    st.info("Create an account or log in from the sidebar to unlock stock predictions and reports.")

def show_home_dashboard():
    page_header(
        "🏠 Market dashboard",
        "A quick view of major-market movers. Prices are indicative and may be delayed.",
    )
    refresh = st.button("↻ Refresh market data", type="primary")
    st.caption("Market overview is loaded on demand and cached by the data provider.")

    if refresh or "dashboard_movers" not in st.session_state:
        try:
            with st.spinner("Loading market overview..."):
                response = api_request("GET", "/stocks/top-movers")
                response.raise_for_status()
                st.session_state["dashboard_movers"] = response.json()
                st.session_state["dashboard_movers_loaded_at"] = datetime.now()
        except (requests.RequestException, ValueError) as error:
            show_api_error("Loading market data", response=locals().get("response"), error=error)
            return

    movers = st.session_state["dashboard_movers"]
    gainers = movers.get("gainers", [])
    losers = movers.get("losers", [])
    stocks = movers.get("all_stocks", [])

    if not stocks:
        st.info("The market-data provider did not return any stocks. Try refreshing shortly.")
        return

    market = pd.DataFrame(stocks)
    if not {"ticker", "current_price", "change_percent"}.issubset(market.columns):
        st.warning("The market provider returned data in an unexpected format.")
        return
    market["change_percent"] = pd.to_numeric(market["change_percent"], errors="coerce")
    market["current_price"] = pd.to_numeric(market["current_price"], errors="coerce")
    market = market.dropna(subset=["change_percent", "current_price"])

    metric_columns = st.columns(3)
    metric_columns[0].metric("Stocks covered", f"{len(market):,}")
    metric_columns[1].metric(
        "Top gainer",
        gainers[0]["ticker"] if gainers else "—",
        f"{gainers[0]['change_percent']:+.2f}%" if gainers else None,
    )
    metric_columns[2].metric(
        "Top decliner",
        losers[0]["ticker"] if losers else "—",
        f"{losers[0]['change_percent']:+.2f}%" if losers else None,
        delta_color="inverse",
    )

    winners_tab, decliners_tab, market_tab = st.tabs(
        ["🚀 Gainers", "📉 Decliners", "📊 Market overview"]
    )
    with winners_tab:
        if gainers:
            st.dataframe(
                pd.DataFrame(gainers).rename(columns={
                    "ticker": "Ticker",
                    "name": "Company",
                    "current_price": "Price ($)",
                    "change_percent": "Change (%)",
                }),
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.info("No positive movers were returned.")
    with decliners_tab:
        if losers:
            st.dataframe(
                pd.DataFrame(losers).rename(columns={
                    "ticker": "Ticker",
                    "name": "Company",
                    "current_price": "Price ($)",
                    "change_percent": "Change (%)",
                }),
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.info("No negative movers were returned.")
    with market_tab:
        filter_column, sort_column, count_column = st.columns([2, 2, 1])
        with filter_column:
            search = st.text_input(
                "Filter by ticker", key="dashboard_ticker_filter",
                placeholder="e.g. AAPL",
            ).strip().upper()
        with sort_column:
            order = st.selectbox(
                "Sort by performance",
                ["Biggest gainers", "Biggest decliners"],
                key="dashboard_sort_order",
            )
        with count_column:
            limit = st.selectbox(
                "Rows", [10, 25, 50, "All"], key="dashboard_row_limit"
            )

        filtered = market.copy()
        if search:
            filtered = filtered[
                filtered["ticker"].astype(str).str.upper().str.contains(search, na=False)
            ]
        filtered = filtered.sort_values(
            "change_percent", ascending=order == "Biggest decliners"
        )
        if limit != "All":
            filtered = filtered.head(limit)
        display = filtered.rename(columns={
            "ticker": "Ticker",
            "name": "Company",
            "current_price": "Price ($)",
            "change_percent": "Change (%)",
        })
        display_columns = [
            column for column in ["Ticker", "Company", "Price ($)", "Change (%)"]
            if column in display.columns
        ]
        st.dataframe(
            display[display_columns].style.format(
                {"Price ($)": "${:,.2f}", "Change (%)": "{:+.2f}%"},
                na_rep="—",
            ),
            hide_index=True,
            use_container_width=True,
        )
        if not filtered.empty:
            choices = filtered["ticker"].astype(str).tolist()
            selected_ticker = st.selectbox(
                "Choose a ticker to analyze",
                choices,
                key="dashboard_selected_ticker",
            )
            st.button(
                "Open stock analysis",
                key="dashboard_open_analysis",
                on_click=open_stock_analysis,
                args=(selected_ticker,),
            )
        else:
            st.info("No stocks match that filter.")

    loaded_at = st.session_state.get("dashboard_movers_loaded_at")
    if loaded_at:
        st.caption(f"Loaded locally at {loaded_at:%Y-%m-%d %H:%M}. Provider data may be cached.")

def show_single_stock_analysis():
    page_header(
        "📊 Single-stock analysis",
        "Choose a ticker and time range to explore prices, volume, and technical indicators.",
    )
    with st.form("single_stock_analysis_form"):
        ticker_col, period_col, chart_col, submit_col = st.columns([2, 1, 1.5, 1])
        with ticker_col:
            ticker = st.text_input(
                "Ticker symbol",
                key="analysis_ticker_input",
                placeholder="AAPL, MSFT, TSLA",
            ).strip().upper()
        with period_col:
            period = st.selectbox(
                "History", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3,
                key="analysis_period",
            )
        with chart_col:
            chart_type = st.selectbox(
                "Chart style", ["Candlestick", "Line"], key="analysis_chart_type"
            )
        with submit_col:
            st.write("")
            st.write("")
            submitted = st.form_submit_button(
                "Analyze", type="primary", use_container_width=True
            )

    if submitted:
        if not ticker:
            st.warning("Enter a stock ticker to continue.")
            return
        try:
            with st.spinner(f"Loading {ticker} analysis..."):
                info_response = api_request("GET", f"/stocks/search/{ticker}")
                info_response.raise_for_status()
                stock_info = info_response.json()
                history_response = api_request(
                    "GET", f"/stocks/history/{ticker}", params={"period": period}
                )
                history_response.raise_for_status()
                history = history_response.json()
                indicators_response = api_request(
                    "GET", f"/stocks/indicators/{ticker}", params={"period": period}
                )
                indicators_response.raise_for_status()
                indicators = indicators_response.json()
            st.session_state["analysis_result"] = {
                "ticker": ticker,
                "period": period,
                "chart_type": chart_type,
                "info": stock_info,
                "history": history,
                "indicators": indicators,
            }
        except (requests.RequestException, ValueError) as error:
            show_api_error(
                f"Loading {ticker} analysis",
                response=locals().get("info_response")
                if getattr(error, "response", None) is None
                else error.response,
                error=error if getattr(error, "response", None) is None else None,
            )
            return

    result = st.session_state.get("analysis_result")
    if not result:
        st.info("Enter a ticker and press **Analyze** to load its market data.")
        return

    ticker = result["ticker"]
    info = result["info"]
    prices = pd.DataFrame(result["history"])
    if prices.empty:
        st.info(f"No price history is available for {ticker} in this period.")
        return
    prices["date"] = pd.to_datetime(prices["date"])
    prices = prices.sort_values("date")
    first_close = float(prices["close"].iloc[0])
    latest_close = float(prices["close"].iloc[-1])
    delta = (latest_close / first_close - 1) * 100 if first_close else 0

    st.subheader(f"{info.get('name', ticker)} · {ticker}")
    metric_cols = st.columns(4)
    metric_cols[0].metric("Latest close", f"${latest_close:,.2f}", f"{delta:+.2f}%")
    metric_cols[1].metric("Period high", f"${prices['high'].max():,.2f}")
    metric_cols[2].metric("Period low", f"${prices['low'].min():,.2f}")
    metric_cols[3].metric("Average volume", f"{prices['volume'].mean():,.0f}")

    selected_chart = st.radio(
        "Display", ["Price", "Volume", "Indicators"],
        horizontal=True, key="analysis_display",
    )
    if selected_chart == "Price":
        if result["chart_type"] == "Candlestick":
            figure = go.Figure(go.Candlestick(
                x=prices["date"], open=prices["open"], high=prices["high"],
                low=prices["low"], close=prices["close"], name=ticker,
            ))
        else:
            figure = go.Figure(go.Scatter(
                x=prices["date"], y=prices["close"], mode="lines",
                name="Close", line={"color": "#4F8BF9", "width": 2},
            ))
        figure.update_layout(
            title=f"{ticker} price · {result['period']}",
            xaxis_title="Date", yaxis_title="Price (USD)",
            height=480, hovermode="x unified",
            margin={"t": 55, "b": 20, "l": 10, "r": 10},
        )
        figure.update_xaxes(rangeslider_visible=True)
        st.plotly_chart(figure, use_container_width=True)
    elif selected_chart == "Volume":
        figure = go.Figure(go.Bar(
            x=prices["date"], y=prices["volume"], name="Volume",
            marker_color="#4F8BF9",
        ))
        figure.update_layout(
            title=f"{ticker} trading volume", xaxis_title="Date",
            yaxis_title="Shares", height=400, hovermode="x unified",
        )
        st.plotly_chart(figure, use_container_width=True)
    else:
        indicators = pd.DataFrame(result["indicators"])
        if indicators.empty:
            st.info("Technical indicators are not available for this period.")
        else:
            indicator_columns = [
                name for name in ["rsi", "macd", "sma_20", "sma_50", "momentum"]
                if name in indicators.columns and indicators[name].notna().any()
            ]
            if not indicator_columns:
                st.info("No technical indicators are available for this period.")
            else:
                choice = st.selectbox(
                    "Indicator", indicator_columns,
                    format_func=lambda name: name.replace("_", " ").upper(),
                    key="analysis_indicator_choice",
                )
                series = indicators[choice].dropna()
                figure = go.Figure(go.Scatter(
                    x=prices["date"].tail(len(indicators)).reset_index(drop=True),
                    y=indicators[choice].reset_index(drop=True),
                    mode="lines",
                    name=choice.replace("_", " ").upper(),
                ))
                if choice == "rsi":
                    figure.add_hline(y=70, line_dash="dash", line_color="#ef4444")
                    figure.add_hline(y=30, line_dash="dash", line_color="#22c55e")
                figure.update_layout(
                    title=f"{ticker} · {choice.replace('_', ' ').upper()}",
                    xaxis_title="Date", height=380, hovermode="x unified",
                )
                st.plotly_chart(figure, use_container_width=True)

    with st.expander("View historical price data"):
        display = prices.rename(columns={
            "date": "Date", "open": "Open", "high": "High",
            "low": "Low", "close": "Close", "volume": "Volume",
        })
        st.dataframe(display, hide_index=True, use_container_width=True)
        st.download_button(
            "Download price data (CSV)",
            data=prices.to_csv(index=False).encode("utf-8"),
            file_name=f"{ticker}_{result['period']}_prices.csv",
            mime="text/csv",
        )

def show_comparison():
    page_header(
        "⚖️ Company comparison",
        "Compare the percentage performance of 2–5 tickers over the same period.",
    )
    with st.form("comparison_form"):
        tickers_input = st.text_input(
            "Tickers, comma separated",
            value=st.session_state.get("comparison_tickers", "AAPL, MSFT, GOOGL"),
            key="comparison_tickers",
            help="Use between two and five unique ticker symbols.",
        )
        period = st.selectbox(
            "Comparison period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=3, key="comparison_period",
        )
        submitted = st.form_submit_button("Compare stocks", type="primary")

    if submitted:
        tickers = list(dict.fromkeys(
            ticker.strip().upper()
            for ticker in tickers_input.split(",")
            if ticker.strip()
        ))
        if not 2 <= len(tickers) <= 5:
            st.warning("Enter between two and five unique ticker symbols.")
            return
        try:
            with st.spinner(f"Comparing {', '.join(tickers)}..."):
                response = api_request(
                    "POST", "/stocks/compare",
                    json={"tickers": tickers, "period": period},
                )
                response.raise_for_status()
                comparison = response.json()
            st.session_state["comparison_result"] = {
                "period": period,
                "data": comparison.get("data", {}),
            }
        except (requests.RequestException, ValueError) as error:
            show_api_error(
                "Comparing stocks",
                response=getattr(error, "response", None),
                error=error if getattr(error, "response", None) is None else None,
            )
            return

    result = st.session_state.get("comparison_result")
    if not result:
        st.info("Choose your tickers and period, then select **Compare stocks**.")
        return

    chart_mode = st.radio(
        "Compare using", ["Percentage return", "Closing price"],
        horizontal=True, key="comparison_chart_mode",
        help="Percentage return starts each ticker at 0%, so differently priced stocks are comparable.",
    )
    figure = go.Figure()
    comparison_rows = []
    for ticker, values in result["data"].items():
        frame = pd.DataFrame(values)
        if frame.empty or not {"date", "close"}.issubset(frame.columns):
            continue
        frame["date"] = pd.to_datetime(frame["date"])
        frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
        frame = frame.dropna(subset=["date", "close"]).sort_values("date")
        if frame.empty:
            continue
        y_values = (
            (frame["close"] / frame["close"].iloc[0] - 1) * 100
            if chart_mode == "Percentage return"
            else frame["close"]
        )
        figure.add_trace(go.Scatter(
            x=frame["date"], y=y_values, mode="lines", name=ticker,
            hovertemplate="%{x|%Y-%m-%d}<br>%{y:.2f}<extra>" + ticker + "</extra>",
        ))
        comparison_rows.append({
            "Ticker": ticker,
            "Start price ($)": frame["close"].iloc[0],
            "Latest price ($)": frame["close"].iloc[-1],
            "Return (%)": (frame["close"].iloc[-1] / frame["close"].iloc[0] - 1) * 100,
        })
    if not comparison_rows:
        st.info("No comparison history was returned. Verify the tickers and try again.")
        return
    figure.update_layout(
        title=f"Stock performance · {result['period']}",
        xaxis_title="Date",
        yaxis_title="Return (%)" if chart_mode == "Percentage return" else "Price (USD)",
        height=500, hovermode="x unified", legend_title="Ticker",
    )
    if chart_mode == "Percentage return":
        figure.add_hline(y=0, line_dash="dot", line_color="gray")
    st.plotly_chart(figure, use_container_width=True)
    summary = pd.DataFrame(comparison_rows).sort_values("Return (%)", ascending=False)
    st.dataframe(
        summary.style.format({
            "Start price ($)": "${:,.2f}",
            "Latest price ($)": "${:,.2f}",
            "Return (%)": "{:+.2f}%",
        }),
        hide_index=True, use_container_width=True,
    )
    st.download_button(
        "Download comparison summary (CSV)",
        data=summary.to_csv(index=False).encode("utf-8"),
        file_name=f"stock_comparison_{result['period']}.csv",
        mime="text/csv",
    )

def show_prediction():
    page_header(
        "🔮 Stock predictions",
        "Train models or request an estimate for one or more tickers. Results are uncertain and not financial advice.",
    )

    # Tabs for different prediction modes
    tab1, tab2, tab3, tab4 = st.tabs(["Single Stock", "Multiple Stocks", "Ensemble", "Forecast"])

    with tab1:
        st.subheader("Single Stock Prediction")
        col1, col2 = st.columns([1, 1])

        with col1:
            ticker = st.text_input(
                "Stock Ticker", key="single_prediction_ticker",
                placeholder="AAPL",
            ).strip().upper()

        with col2:
            model = st.selectbox("Model", ["linear", "rf", "xgb", "lstm"])

        days_options = st.multiselect("Prediction Days", [7, 15, 30], default=[7], key="single_days")

        if st.button("Train Model", key="train_single"):
            if not ticker:
                st.warning("Enter a ticker symbol before training a model.")
                return
            try:
                with st.spinner(f"Training {model} for {ticker}..."):
                    response = api_request(
                    "POST", f"/models/train/{ticker}", authenticated=True,
                    json={"ticker": ticker, "models": [model]},
                    )
                    response.raise_for_status()

                result = response.json()
                st.session_state["single_training_result"] = {
                    "ticker": ticker, "model": model, "result": result
                }
                st.success(f"Model trained successfully! Best model: {result['best_model']}")
            except (requests.RequestException, ValueError) as error:
                show_api_error(
                    "Model training", response=getattr(error, "response", None),
                    error=error if getattr(error, "response", None) is None else None,
                )

        if st.button("Make Prediction", key="make_single"):
            if not ticker:
                st.warning("Enter a ticker symbol before making a prediction.")
            elif not days_options:
                st.warning("Select at least one prediction horizon.")
            else:
                predictions = {}
                try:
                    with st.spinner(f"Generating predictions for {ticker}..."):
                        for days in days_options:
                            response = api_request(
                                "POST", f"/models/predict/{ticker}",
                                authenticated=True,
                                json={
                                    "ticker": ticker,
                                    "model_name": model,
                                    "days_ahead": days,
                                },
                            )
                            response.raise_for_status()
                            predictions[days] = response.json()["predicted_price"]
                    st.session_state["single_prediction_result"] = {
                        "ticker": ticker, "model": model, "predictions": predictions
                    }
                except (requests.RequestException, ValueError, KeyError) as error:
                    show_api_error(
                        "Stock prediction", response=getattr(error, "response", None),
                        error=error if getattr(error, "response", None) is None else None,
                    )
                if predictions:
                    st.subheader("Predictions")
                    cols = st.columns(len(predictions))
                    for column, (days, price) in zip(cols, predictions.items()):
                        column.metric(f"{days} days", f"${price:,.2f}")

        training = st.session_state.get("single_training_result")
        if training and training["ticker"] == ticker:
            result = training["result"]
            st.caption(f"Last trained model: {training['model']} for {ticker}")
            metrics = result.get("metrics", {}).get(training["model"])
            if metrics:
                cols = st.columns(4)
                for col, (name, value) in zip(cols, metrics.items()):
                    col.metric(name.replace("_", " ").upper(), f"{value:.4f}")
        prediction_result = st.session_state.get("single_prediction_result")
        if prediction_result and prediction_result["ticker"] == ticker:
            st.caption(f"Last prediction set uses the {prediction_result['model']} model.")

    with tab2:
        st.subheader("Multiple Stock Predictions")
        tickers_input = st.text_area(
            "Enter tickers (comma-separated)",
            "AAPL, MSFT, GOOGL",
            key="batch_tickers_input",
            help="Enter up to 20 ticker symbols.",
        )
        model_batch = st.selectbox("Model", ["linear", "rf", "xgb", "lstm"], key="batch_model")
        days_batch = st.select_slider("Days Ahead", options=list(range(1, 61)), value=7, key="batch_days")

        if st.button("Predict Multiple Stocks", key="predict_batch"):
            try:
                tickers_list = list(dict.fromkeys(
                    t.strip().upper() for t in tickers_input.split(",") if t.strip()
                ))
                if not tickers_list:
                    st.warning("Enter at least one ticker symbol.")
                    return
                if len(tickers_list) > 20:
                    st.warning("Submit no more than 20 tickers at once.")
                    return
                with st.spinner(f"Predicting {len(tickers_list)} stocks..."):
                    response = api_request(
                    "POST", "/models/predict-batch", authenticated=True,
                    json={
                        "tickers": tickers_list,
                        "model_name": model_batch,
                        "days_ahead": days_batch
                    })
                    response.raise_for_status()
                    result = response.json()
                st.session_state["batch_prediction_result"] = result
                st.success(f"Predictions completed for {len(tickers_list)} stocks")

                pred_data = []
                for result_ticker, pred in result["predictions"].items():
                    pred_data.append({
                        "Ticker": result_ticker,
                        "Status": "Complete" if pred.get("success") else "Failed",
                        "Predicted Price": pred.get("prediction"),
                        "Days Ahead": pred.get("days_ahead", days_batch),
                        "Details": pred.get("error", ""),
                    })
                if pred_data:
                    df = pd.DataFrame(pred_data)
                    st.dataframe(
                        df.style.format({"Predicted Price": "${:,.2f}"}),
                        hide_index=True, use_container_width=True,
                    )
                    st.download_button(
                        "Download batch results (CSV)",
                        df.to_csv(index=False).encode("utf-8"),
                        file_name="batch_predictions.csv",
                        mime="text/csv",
                    )
                else:
                    st.info("No results were returned for those tickers.")
            except (requests.RequestException, ValueError, KeyError) as error:
                show_api_error(
                    "Batch prediction", response=getattr(error, "response", None),
                    error=error if getattr(error, "response", None) is None else None,
                )

    with tab3:
        st.subheader("Ensemble Prediction (Multiple Models)")
        ticker_ens = st.text_input(
            "Stock Ticker", key="ensemble_ticker", placeholder="AAPL"
        ).strip().upper()
        days_ens = st.select_slider("Days Ahead", options=list(range(1, 61)), value=7, key="ensemble_days")

        if st.button("Make Ensemble Prediction", key="predict_ensemble"):
            if not ticker_ens:
                st.warning("Enter a ticker symbol before requesting an ensemble prediction.")
                return
            try:
                with st.spinner(f"Calculating ensemble for {ticker_ens}..."):
                    response = api_request(
                        "POST", f"/models/ensemble/{ticker_ens}",
                        authenticated=True,
                        json={"ticker": ticker_ens, "model_name": "linear", "days_ahead": days_ens},
                    )
                    response.raise_for_status()
                    result = response.json()
                st.session_state["ensemble_result"] = {
                    "ticker": ticker_ens, "result": result
                }
                st.success(f"Ensemble prediction for {ticker_ens}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Ensemble Price", f"${result['ensemble_prediction']:.2f}")
                with col2:
                    st.metric("Std Deviation", f"${result['std_deviation']:.2f}")
                with col3:
                    st.metric(
                        "Confidence Range",
                        f"${result['lower_bound']:.2f} - ${result['upper_bound']:.2f}",
                    )

                st.subheader("Individual Model Predictions")
                model_preds = []
                for model_name, model_data in result["model_predictions"].items():
                    if "error" not in model_data:
                        model_preds.append({
                            "Model": model_name,
                            "Predicted Price": model_data["price"],
                        })
                if model_preds:
                    df = pd.DataFrame(model_preds)
                    st.dataframe(
                        df.style.format({"Predicted Price": "${:,.2f}"}),
                        hide_index=True, use_container_width=True,
                    )

            except (requests.RequestException, ValueError, KeyError) as error:
                show_api_error(
                    "Ensemble prediction", response=getattr(error, "response", None),
                    error=error if getattr(error, "response", None) is None else None,
                )

    with tab4:
        st.subheader("Future Price Forecast")
        ticker_forecast = st.text_input(
            "Stock Ticker", key="forecast_ticker", placeholder="AAPL"
        ).strip().upper()
        model_forecast = st.selectbox("Model", ["linear", "rf", "xgb", "lstm"], key="forecast_model")
        days_forecast = st.slider("Forecast Days", 7, 90, 30, key="forecast_days")

        if st.button("Generate Forecast", key="generate_forecast"):
            if not ticker_forecast:
                st.warning("Enter a ticker symbol before generating a forecast.")
                return
            try:
                with st.spinner(f"Generating {days_forecast}-day forecast for {ticker_forecast}..."):
                    response = api_request(
                        "POST", f"/models/forecast/{ticker_forecast}",
                        authenticated=True,
                        params={"days": days_forecast},
                        json={"ticker": ticker_forecast, "model_name": model_forecast, "days_ahead": days_forecast},
                    )
                    response.raise_for_status()
                    result = response.json()
                st.session_state["forecast_result"] = {
                    "ticker": ticker_forecast, "result": result
                }
                st.success(f"Forecast generated for {ticker_forecast}")

                forecast_df = pd.DataFrame(result["forecast"])
                forecast_df["date"] = pd.to_datetime(forecast_df["date"])
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=forecast_df["date"],
                    y=forecast_df["predicted_price"],
                    mode="lines+markers",
                    name="Predicted price",
                    line={"color": "#4F8BF9", "width": 2},
                ))
                if {"lower_bound", "upper_bound"}.issubset(forecast_df.columns):
                    fig.add_trace(go.Scatter(
                        x=forecast_df["date"], y=forecast_df["upper_bound"],
                        mode="lines", line={"width": 0}, showlegend=False,
                    ))
                    fig.add_trace(go.Scatter(
                        x=forecast_df["date"], y=forecast_df["lower_bound"],
                        mode="lines", fill="tonexty", name="Confidence interval",
                        line={"width": 0}, fillcolor="rgba(79,139,249,0.18)",
                    ))
                fig.update_layout(
                    title=f"{ticker_forecast} price forecast",
                    xaxis_title="Date", yaxis_title="Price (USD)",
                    hovermode="x unified", height=500,
                )
                st.plotly_chart(fig, use_container_width=True)
                st.subheader("Forecast details")
                forecast_display = forecast_df.copy()
                forecast_display["date"] = forecast_display["date"].dt.strftime("%Y-%m-%d")
                st.dataframe(
                    forecast_display, hide_index=True, use_container_width=True
                )
                st.download_button(
                    "Download forecast (CSV)",
                    forecast_display.to_csv(index=False).encode("utf-8"),
                    file_name=f"{ticker_forecast}_forecast.csv",
                    mime="text/csv",
                )
            except (requests.RequestException, ValueError, KeyError) as error:
                show_api_error(
                    "Forecast generation", response=getattr(error, "response", None),
                    error=error if getattr(error, "response", None) is None else None,
                )

def show_history():
    page_header(
        "📋 Prediction history",
        "Review saved forecasts, search by ticker, and download your history.",
    )
    refresh_col, _ = st.columns([1, 4])
    with refresh_col:
        refresh = st.button("↻ Refresh history")
    if refresh or "prediction_history" not in st.session_state:
        try:
            with st.spinner("Loading prediction history..."):
                response = api_request("GET", "/history", authenticated=True)
                response.raise_for_status()
                st.session_state["prediction_history"] = response.json()
        except (requests.RequestException, ValueError) as error:
            show_api_error(
                "Loading prediction history",
                response=getattr(error, "response", None),
                error=error if getattr(error, "response", None) is None else None,
            )
            return

    history = st.session_state["prediction_history"]
    if not history:
        st.info("No predictions have been saved yet. Try making a prediction first.")
        return
    frame = pd.DataFrame(history)
    if "created_at" in frame.columns:
        frame["created_at"] = pd.to_datetime(frame["created_at"], errors="coerce")
    filters = st.columns([2, 1, 1])
    with filters[0]:
        ticker_filter = st.text_input(
            "Filter by ticker", key="history_ticker_filter",
            placeholder="e.g. AAPL",
        ).strip().upper()
    with filters[1]:
        models = ["All"] + sorted(frame["model_name"].dropna().astype(str).unique()) if "model_name" in frame else ["All"]
        model_filter = st.selectbox("Model", models, key="history_model_filter")
    with filters[2]:
        sort_order = st.selectbox(
            "Order", ["Newest first", "Oldest first"], key="history_sort_order"
        )

    filtered = frame.copy()
    if ticker_filter and "ticker" in filtered:
        filtered = filtered[
            filtered["ticker"].astype(str).str.upper().str.contains(ticker_filter, na=False)
        ]
    if model_filter != "All" and "model_name" in filtered:
        filtered = filtered[filtered["model_name"] == model_filter]
    if "created_at" in filtered:
        filtered = filtered.sort_values(
            "created_at", ascending=sort_order == "Oldest first", na_position="last"
        )
        filtered["created_at"] = filtered["created_at"].dt.strftime("%Y-%m-%d %H:%M")
    display_cols = [
        column for column in [
            "ticker", "model_name", "predicted_price", "days_ahead", "created_at"
        ] if column in filtered.columns
    ]
    st.caption(f"Showing {len(filtered)} of {len(frame)} saved predictions")
    if filtered.empty:
        st.info("No predictions match these filters.")
        return
    st.dataframe(
        filtered[display_cols].rename(columns={
            "ticker": "Ticker",
            "model_name": "Model",
            "predicted_price": "Predicted price ($)",
            "days_ahead": "Days ahead",
            "created_at": "Created at",
        }).style.format({"Predicted price ($)": "${:,.2f}"}),
        hide_index=True,
        use_container_width=True,
    )
    st.download_button(
        "Download filtered history (CSV)",
        data=filtered[display_cols].to_csv(index=False).encode("utf-8"),
        file_name="prediction_history.csv",
        mime="text/csv",
    )

def show_reports():
    page_header(
        "📄 Reports & downloads",
        "Generate a historical-data report for a ticker and download it as CSV or PDF.",
    )
    with st.form("report_form"):
        ticker = st.text_input(
            "Ticker symbol", key="report_ticker", placeholder="AAPL"
        ).strip().upper()
        format_type = st.selectbox(
            "File format", ["csv", "pdf"], key="report_format"
        )
        submitted = st.form_submit_button("Generate report", type="primary")

    if submitted:
        if not ticker:
            st.warning("Enter a ticker symbol to generate a report.")
            return
        try:
            with st.spinner(f"Building {ticker} report..."):
                response = api_request(
                    "GET",
                    f"/report/{ticker}",
                    authenticated=True,
                    params={"format": format_type},
                )
                response.raise_for_status()
            st.session_state["report_file"] = {
                "ticker": ticker,
                "format": format_type,
                "content": response.content,
            }
        except requests.RequestException as error:
            show_api_error(
                "Report generation",
                response=getattr(error, "response", None),
                error=error if getattr(error, "response", None) is None else None,
            )
    report = st.session_state.get("report_file")
    if report and report["ticker"] == ticker and report["format"] == format_type:
        file_size = len(report["content"])
        st.success(f"Your {ticker} {format_type.upper()} report is ready ({file_size:,} bytes).")
        st.download_button(
            label=f"Download {ticker} report",
            data=report["content"],
            file_name=f"{ticker}_report.{format_type}",
            mime="text/csv" if format_type == "csv" else "application/pdf",
            type="primary",
        )

def show_sector_analysis():
    page_header(
        "🏢 Sector analysis",
        "Explore average sector performance and the constituent stocks returned by the market-data provider.",
    )
    refresh = st.button("↻ Refresh sector data")
    if refresh or "sector_analysis_data" not in st.session_state:
        try:
            with st.spinner("Loading sector performance..."):
                response = api_request("GET", "/stocks/sector-analysis")
                response.raise_for_status()
                st.session_state["sector_analysis_data"] = response.json()
        except (requests.RequestException, ValueError) as error:
            show_api_error(
                "Loading sector data",
                response=getattr(error, "response", None),
                error=error if getattr(error, "response", None) is None else None,
            )
            return

    sectors = st.session_state["sector_analysis_data"]
    if not sectors:
        st.info("No sector performance data is available right now.")
        return
    sectors = sorted(
        sectors,
        key=lambda sector: sector.get("average_performance", 0),
        reverse=True,
    )
    sector_names = ["All sectors"] + [
        sector["sector"] for sector in sectors if sector.get("sector")
    ]
    selected_sector = st.selectbox(
        "Focus on a sector", sector_names, key="sector_analysis_filter"
    )
    overview = pd.DataFrame([
        {
            "Sector": sector.get("sector", "Unknown"),
            "Average performance (%)": sector.get("average_performance"),
            "Stocks": len(sector.get("stocks", [])),
        }
        for sector in sectors
    ])
    st.dataframe(
        overview.style.format({"Average performance (%)": "{:+.2f}%"}),
        hide_index=True,
        use_container_width=True,
    )
    displayed = sectors if selected_sector == "All sectors" else [
        sector for sector in sectors if sector.get("sector") == selected_sector
    ]
    for sector in displayed:
        performance = sector.get("average_performance")
        with st.expander(
            f"{sector.get('sector', 'Sector')} · "
            f"{performance:+.2f}%" if performance is not None else sector.get("sector", "Sector"),
            expanded=selected_sector != "All sectors",
        ):
            cols = st.columns(2)
            cols[0].metric(
                "Average performance",
                f"{performance:+.2f}%" if performance is not None else "Unavailable",
            )
            stocks_df = pd.DataFrame(sector.get("stocks", []))
            if stocks_df.empty:
                st.info("No constituent stock data is available.")
            else:
                cols[1].metric("Stocks covered", len(stocks_df))
                available_cols = [
                    name for name in [
                        "ticker", "name", "current_price", "change_percent"
                    ] if name in stocks_df.columns
                ]
                st.dataframe(
                    stocks_df[available_cols].rename(columns={
                        "ticker": "Ticker",
                        "name": "Company",
                        "current_price": "Price ($)",
                        "change_percent": "Change (%)",
                    }),
                    hide_index=True,
                    use_container_width=True,
                )

def show_stock_screener():
    page_header(
        "🔍 Stock screener",
        "Search for a company or browse and filter the active exchange listing.",
    )
    search_tab, listing_tab = st.tabs(
        ["Search by name or ticker", "Browse listed stocks"]
    )

    with search_tab:
        with st.form("ticker_search_form"):
            query = st.text_input(
                "Company name or ticker",
                key="ticker_search_query",
                placeholder="Apple, TSLA, Microsoft",
            ).strip()
            submitted = st.form_submit_button("Search", type="primary")
        if submitted:
            if not query:
                st.warning("Enter a company name or ticker to search.")
            else:
                try:
                    with st.spinner(f"Searching for {query}..."):
                        response = api_request(
                            "GET", "/stocks/ticker-search", params={"q": query}
                        )
                        response.raise_for_status()
                        st.session_state["ticker_search_results"] = {
                            "query": query,
                            "results": response.json().get("results", []),
                        }
                except (requests.RequestException, ValueError) as error:
                    show_api_error(
                        "Ticker search",
                        response=getattr(error, "response", None),
                        error=error if getattr(error, "response", None) is None else None,
                    )
        search_result = st.session_state.get("ticker_search_results")
        if search_result and search_result["query"] == query:
            results = search_result["results"]
            if not results:
                st.info("No matching tickers found. Try a different company name or symbol.")
            else:
                frame = pd.DataFrame(results)
                st.caption(f"{len(results)} match(es) for “{search_result['query']}”")
                st.dataframe(
                    frame.rename(columns=lambda name: name.replace("_", " ").title()),
                    hide_index=True,
                    use_container_width=True,
                )
                ticker_column = next(
                    (column for column in ["symbol", "ticker"] if column in frame),
                    None,
                )
                if ticker_column:
                    symbols = frame[ticker_column].dropna().astype(str).tolist()
                    if symbols:
                        selected = st.selectbox(
                            "Select a result to analyze",
                            symbols,
                            key="ticker_search_selected",
                        )
                        st.button(
                            "Open stock analysis",
                            key="ticker_search_analyze",
                            on_click=open_stock_analysis,
                            args=(selected,),
                        )

    with listing_tab:
        st.info(
            "The full active listing comes from Alpha Vantage and may be large or rate limited."
        )
        load_col, refresh_col = st.columns([1, 1])
        with load_col:
            load_listing = st.button(
                "Load active listing", type="primary", key="load_stock_listing"
            )
        with refresh_col:
            refresh_listing = st.button("Refresh listing", key="refresh_stock_listing")
        if (load_listing or refresh_listing
                or "active_stock_listing" not in st.session_state):
            try:
                with st.spinner("Fetching active exchange listing..."):
                    response = api_request(
                        "GET", "/stocks/listed", params={"state": "active"}
                    )
                    response.raise_for_status()
                    st.session_state["active_stock_listing"] = response.json()
            except (requests.RequestException, ValueError) as error:
                show_api_error(
                    "Loading active listing",
                    response=getattr(error, "response", None),
                    error=error if getattr(error, "response", None) is None else None,
                )
        listing = st.session_state.get("active_stock_listing")
        if not listing:
            st.info("Select **Load active listing** to browse listed stocks.")
        else:
            frame = pd.DataFrame(listing.get("stocks", []))
            if frame.empty:
                st.warning("The provider returned no active listings.")
            else:
                filter_cols = st.columns([2, 2, 3, 1])
                exchanges = (
                    ["All"] + sorted(frame["exchange"].dropna().astype(str).unique())
                    if "exchange" in frame else ["All"]
                )
                asset_types = (
                    ["All"] + sorted(frame["assetType"].dropna().astype(str).unique())
                    if "assetType" in frame else ["All"]
                )
                with filter_cols[0]:
                    selected_exchange = st.selectbox(
                        "Exchange", exchanges, key="listing_exchange_filter"
                    )
                with filter_cols[1]:
                    selected_type = st.selectbox(
                        "Asset type", asset_types, key="listing_type_filter"
                    )
                with filter_cols[2]:
                    listing_query = st.text_input(
                        "Filter results", key="listing_text_filter",
                        placeholder="Search ticker or company",
                    ).strip().lower()
                with filter_cols[3]:
                    row_limit = st.selectbox(
                        "Rows", [25, 50, 100, "All"], key="listing_row_limit"
                    )

                filtered = frame.copy()
                if selected_exchange != "All" and "exchange" in filtered:
                    filtered = filtered[filtered["exchange"] == selected_exchange]
                if selected_type != "All" and "assetType" in filtered:
                    filtered = filtered[filtered["assetType"] == selected_type]
                if listing_query:
                    searchable = [
                        column for column in ["symbol", "name", "exchange"]
                        if column in filtered
                    ]
                    if searchable:
                        match = filtered[searchable].astype(str).apply(
                            lambda column: column.str.lower().str.contains(
                                listing_query, na=False
                            )
                        ).any(axis=1)
                        filtered = filtered[match]
                st.caption(
                    f"Showing {len(filtered):,} of {len(frame):,} active listings"
                )
                displayed = filtered if row_limit == "All" else filtered.head(row_limit)
                st.dataframe(
                    displayed,
                    hide_index=True,
                    use_container_width=True,
                )
                st.download_button(
                    "Download filtered listing (CSV)",
                    data=filtered.to_csv(index=False).encode("utf-8"),
                    file_name="active_stock_listing.csv",
                    mime="text/csv",
                )

if __name__ == "__main__":
    main()