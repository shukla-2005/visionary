import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler

def create_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create time-based features from Date column.

    Args:
        df: DataFrame with Date column

    Returns:
        DataFrame with time features
    """
    df = df.copy()

    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df['Year'] = df['Date'].dt.year
        df['Month'] = df['Date'].dt.month
        df['Day'] = df['Date'].dt.day
        df['DayOfWeek'] = df['Date'].dt.dayofweek
        df['DayOfYear'] = df['Date'].dt.dayofyear
        df['WeekOfYear'] = df['Date'].dt.isocalendar().week
        df['Quarter'] = df['Date'].dt.quarter

        # Cyclical encoding for month and day of week
        df['Month_sin'] = np.sin(2 * np.pi * df['Month'] / 12)
        df['Month_cos'] = np.cos(2 * np.pi * df['Month'] / 12)
        df['DayOfWeek_sin'] = np.sin(2 * np.pi * df['DayOfWeek'] / 7)
        df['DayOfWeek_cos'] = np.cos(2 * np.pi * df['DayOfWeek'] / 7)

    return df

def create_price_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create price-based features.

    Args:
        df: DataFrame with OHLC data

    Returns:
        DataFrame with price features
    """
    df = df.copy()

    # Basic price features
    df['Price_Range'] = df['High'] - df['Low']
    df['Price_Change'] = df['Close'] - df['Open']
    df['Body_Size'] = abs(df['Close'] - df['Open'])
    df['Upper_Shadow'] = df['High'] - np.maximum(df['Open'], df['Close'])
    df['Lower_Shadow'] = np.minimum(df['Open'], df['Close']) - df['Low']

    # Returns
    df['Daily_Return'] = df['Close'].pct_change()
    df['Log_Return'] = np.log(df['Close'] / df['Close'].shift(1))

    # Volatility measures
    df['Volatility_5'] = df['Daily_Return'].rolling(window=5).std()
    df['Volatility_10'] = df['Daily_Return'].rolling(window=10).std()
    df['Volatility_20'] = df['Daily_Return'].rolling(window=20).std()

    return df

def create_volume_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create volume-based features.

    Args:
        df: DataFrame with Volume data

    Returns:
        DataFrame with volume features
    """
    df = df.copy()

    # Volume moving averages
    df['Volume_MA_5'] = df['Volume'].rolling(window=5).mean()
    df['Volume_MA_10'] = df['Volume'].rolling(window=10).mean()
    df['Volume_MA_20'] = df['Volume'].rolling(window=20).mean()

    # Volume ratios
    df['Volume_Ratio_5'] = df['Volume'] / df['Volume_MA_5']
    df['Volume_Ratio_10'] = df['Volume'] / df['Volume_MA_10']

    # Volume trends
    df['Volume_Trend_5'] = df['Volume_MA_5'].pct_change(5)
    df['Volume_Trend_10'] = df['Volume_MA_10'].pct_change(10)

    return df

def create_lag_features(df: pd.DataFrame, columns: list, lags: list = [1, 2, 3, 5, 7, 10, 15, 20, 30]) -> pd.DataFrame:
    """
    Create lag features for specified columns.

    Args:
        df: Input DataFrame
        columns: List of columns to create lags for
        lags: List of lag periods

    Returns:
        DataFrame with lag features
    """
    df = df.copy()

    for col in columns:
        if col in df.columns:
            for lag in lags:
                df[f'{col}_Lag_{lag}'] = df[col].shift(lag)

    return df

def create_rolling_features(df: pd.DataFrame, columns: list, windows: list = [5, 10, 20, 30]) -> pd.DataFrame:
    """
    Create rolling statistics features.

    Args:
        df: Input DataFrame
        columns: List of columns to create rolling features for
        windows: List of rolling window sizes

    Returns:
        DataFrame with rolling features
    """
    df = df.copy()

    for col in columns:
        if col in df.columns:
            for window in windows:
                df[f'{col}_Rolling_Mean_{window}'] = df[col].rolling(window=window).mean()
                df[f'{col}_Rolling_Std_{window}'] = df[col].rolling(window=window).std()
                df[f'{col}_Rolling_Min_{window}'] = df[col].rolling(window=window).min()
                df[f'{col}_Rolling_Max_{window}'] = df[col].rolling(window=window).max()

    return df

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Complete feature engineering pipeline.

    Args:
        df: Raw stock data DataFrame

    Returns:
        DataFrame with engineered features
    """
    df = df.copy()

    # Time features
    df = create_time_features(df)

    # Price features
    df = create_price_features(df)

    # Volume features
    df = create_volume_features(df)

    # Lag features for key columns
    key_columns = ['Close', 'Volume', 'Daily_Return']
    df = create_lag_features(df, key_columns)

    # Rolling features
    df = create_rolling_features(df, ['Close', 'Volume'])

    # Drop rows with NaN values
    df = df.dropna()

    return df

def scale_features(X_train: np.ndarray, X_test: np.ndarray, method: str = 'standard') -> tuple:
    """
    Scale features using specified method.

    Args:
        X_train: Training features
        X_test: Test features
        method: Scaling method ('standard' or 'minmax')

    Returns:
        Tuple of (X_train_scaled, X_test_scaled, scaler)
    """
    if method == 'standard':
        scaler = StandardScaler()
    elif method == 'minmax':
        scaler = MinMaxScaler()
    else:
        raise ValueError("Method must be 'standard' or 'minmax'")

    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train_scaled, X_test_scaled, scaler