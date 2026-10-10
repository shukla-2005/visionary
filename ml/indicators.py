import pandas as pd
import numpy as np

def calculate_sma(data: pd.Series, window: int) -> pd.Series:
    """Calculate Simple Moving Average"""
    return data.rolling(window=window).mean()

def calculate_ema(data: pd.Series, window: int) -> pd.Series:
    """Calculate Exponential Moving Average"""
    return data.ewm(span=window, adjust=False).mean()

def calculate_rsi(data: pd.Series, window: int = 14) -> pd.Series:
    """Calculate Relative Strength Index"""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
    """Calculate MACD, Signal line, and Histogram"""
    ema_fast = calculate_ema(data, fast)
    ema_slow = calculate_ema(data, slow)
    macd = ema_fast - ema_slow
    signal_line = calculate_ema(macd, signal)
    histogram = macd - signal_line
    return macd, signal_line, histogram

def calculate_bollinger_bands(data: pd.Series, window: int = 20, num_std: int = 2) -> tuple:
    """Calculate Bollinger Bands"""
    sma = calculate_sma(data, window)
    std = data.rolling(window=window).std()
    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)
    return upper_band, sma, lower_band

def calculate_momentum(data: pd.Series, window: int = 10) -> pd.Series:
    """Calculate Momentum"""
    return data / data.shift(window) - 1

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate all technical indicators for the given DataFrame.

    Args:
        df: DataFrame with OHLC data

    Returns:
        DataFrame with technical indicators
    """
    df = df.copy()

    # Simple Moving Averages
    df['SMA_20'] = calculate_sma(df['Close'], 20)
    df['SMA_50'] = calculate_sma(df['Close'], 50)

    # Exponential Moving Averages
    df['EMA_12'] = calculate_ema(df['Close'], 12)
    df['EMA_26'] = calculate_ema(df['Close'], 26)

    # RSI
    df['RSI'] = calculate_rsi(df['Close'])

    # MACD
    macd, macd_signal, macd_hist = calculate_macd(df['Close'])
    df['MACD'] = macd
    df['MACD_Signal'] = macd_signal
    df['MACD_Hist'] = macd_hist

    # Bollinger Bands
    bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(df['Close'])
    df['BB_Upper'] = bb_upper
    df['BB_Middle'] = bb_middle
    df['BB_Lower'] = bb_lower

    # Momentum
    df['Momentum'] = calculate_momentum(df['Close'])

    return df