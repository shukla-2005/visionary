"""
Data loader for ML training — uses yfinance 1.3.0 as primary source.
"""

import yfinance as yf
import pandas as pd
import datetime
from typing import Optional


def load_stock_data(ticker: str, period: str = "2y") -> Optional[pd.DataFrame]:
    """
    Load historical OHLCV data using yfinance.

    Args:
        ticker: Stock ticker symbol
        period: Time period (e.g., '1y', '2y', '5y')

    Returns:
        DataFrame with columns [Date, Open, High, Low, Close, Volume] or None
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, auto_adjust=True)

        if df.empty:
            print(f"No data returned for {ticker}")
            return None

        # Reset index — makes Date a regular column
        df = df.reset_index()

        # Rename 'Datetime' to 'Date' if needed (intraday intervals)
        if "Datetime" in df.columns and "Date" not in df.columns:
            df = df.rename(columns={"Datetime": "Date"})

        # Strip timezone from Date so downstream code doesn't break
        if isinstance(df["Date"].dtype, pd.DatetimeTZDtype):
            df["Date"] = df["Date"].dt.tz_localize(None)

        required = ["Date", "Open", "High", "Low", "Close", "Volume"]
        if not all(col in df.columns for col in required):
            print(f"Missing required columns for {ticker}: {df.columns.tolist()}")
            return None

        return df[required].copy()

    except Exception as e:
        print(f"Error loading data for {ticker}: {e}")
        return None


def get_stock_info(ticker: str) -> Optional[dict]:
    """
    Get basic stock information using yfinance fast_info.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dictionary with stock info or None if failed
    """
    try:
        stock = yf.Ticker(ticker)
        fi = stock.fast_info
        return {
            "symbol": ticker.upper(),
            "last_price": fi.last_price,
            "year_high": fi.year_high,
            "year_low": fi.year_low,
            "market_cap": fi.market_cap,
            "three_month_avg_volume": fi.three_month_average_volume,
        }
    except Exception as e:
        print(f"Error getting info for {ticker}: {e}")
        return None
