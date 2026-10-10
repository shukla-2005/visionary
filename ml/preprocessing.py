import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from .feature_engineering import engineer_features

def preprocess_data(df: pd.DataFrame, target_column: str = 'Close') -> tuple:
    """
    Preprocess stock data for ML models.

    Args:
        df: DataFrame with stock data (raw — feature engineering is applied here)
        target_column: Column to predict

    Returns:
        Tuple of (X_train, X_test, y_train, y_test, X_scaler, y_scaler)
    """
    # Handle missing values
    df = df.dropna()

    # Engineer features — only done once here; callers must NOT pre-engineer
    df_processed = engineer_features(df)

    # Select features for training (exclude target and date columns)
    feature_columns = [
        col for col in df_processed.columns
        if col != target_column and col != 'Date' and not col.startswith('Date')
    ]
    X = df_processed[feature_columns]
    y = df_processed[target_column]

    # Scale features and target separately
    X_scaler = MinMaxScaler()
    y_scaler = MinMaxScaler()
    
    X_scaled = X_scaler.fit_transform(X)
    y_scaled = y_scaler.fit_transform(y.values.reshape(-1, 1)).flatten()

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_scaled, test_size=0.2, random_state=42, shuffle=False
    )

    return X_train, X_test, y_train, y_test, X_scaler, y_scaler

def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create additional features for ML models.

    Args:
        df: Original DataFrame

    Returns:
        DataFrame with additional features
    """
    df = df.copy()

    # Price-based features
    df['Returns'] = df['Close'].pct_change()
    df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))

    # Moving averages
    df['MA_5'] = df['Close'].rolling(window=5).mean()
    df['MA_10'] = df['Close'].rolling(window=10).mean()
    df['MA_20'] = df['Close'].rolling(window=20).mean()

    # Volatility
    df['Volatility_5'] = df['Returns'].rolling(window=5).std()
    df['Volatility_10'] = df['Returns'].rolling(window=10).std()

    # Volume features
    df['Volume_MA_5'] = df['Volume'].rolling(window=5).mean()
    df['Volume_Ratio'] = df['Volume'] / df['Volume_MA_5']

    # Lag features
    for lag in [1, 2, 3, 5, 10]:
        df[f'Close_Lag_{lag}'] = df['Close'].shift(lag)
        df[f'Volume_Lag_{lag}'] = df['Volume'].shift(lag)

    # Technical indicators (basic)
    df['Price_Range'] = df['High'] - df['Low']
    df['Price_Change'] = df['Close'] - df['Open']

    # Drop rows with NaN values created by rolling windows and lags
    df = df.dropna()
    return df

def prepare_lstm_data(X: np.ndarray, y: np.ndarray, time_steps: int = 60) -> tuple:
    """
    Prepare data for LSTM model.

    Args:
        X: Feature matrix
        y: Target vector
        time_steps: Number of time steps for LSTM

    Returns:
        Tuple of (X_lstm, y_lstm)
    """
    X_lstm, y_lstm = [], []

    for i in range(time_steps, len(X)):
        X_lstm.append(X[i-time_steps:i])
        y_lstm.append(y.iloc[i] if hasattr(y, 'iloc') else y[i])

    return np.array(X_lstm), np.array(y_lstm)