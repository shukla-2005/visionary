import os
import pickle
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from ml.data_loader import load_stock_data
from ml.preprocessing import preprocess_data, prepare_lstm_data
from ml.feature_engineering import engineer_features
from ml.evaluate import evaluate_model
from ml.lstm_model import create_lstm_model, train_lstm_model, save_lstm_model, load_lstm_model

def train_models(ticker: str, models: list = None) -> tuple:
    """
    Train multiple ML models for stock prediction.

    Args:
        ticker: Stock ticker symbol
        models: List of model names to train

    Returns:
        Tuple of (trained_models, metrics)
    """
    if models is None:
        models = ["linear", "rf", "xgb", "lstm"]

    # Load data
    df = load_stock_data(ticker, period="2y")
    if df is None or df.empty:
        raise ValueError(f"No data available for {ticker}")

    # Preprocess data (feature engineering is done inside preprocess_data)
    X_train, X_test, y_train, y_test, X_scaler, y_scaler = preprocess_data(df)

    # Also engineer features separately for LSTM sequence preparation
    df_features = engineer_features(df)

    trained_models = {}
    metrics = {}

    # Train each model
    for model_name in models:
        try:
            if model_name == "linear":
                model = LinearRegression()
                model.fit(X_train, y_train)
                predictions = model.predict(X_test)

            elif model_name == "rf":
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                model.fit(X_train, y_train)
                predictions = model.predict(X_test)

            elif model_name == "xgb":
                model = XGBRegressor(n_estimators=100, random_state=42)
                model.fit(X_train, y_train)
                predictions = model.predict(X_test)

            elif model_name == "lstm":
                # Prepare LSTM data
                X_lstm, y_lstm = prepare_lstm_data(X_train, y_train)
                X_lstm_test, y_lstm_test = prepare_lstm_data(X_test, y_test)

                model = create_lstm_model((X_lstm.shape[1], X_lstm.shape[2]))
                model = train_lstm_model(model, X_lstm, y_lstm, X_lstm_test, y_lstm_test)
                predictions = model.predict(X_lstm_test).flatten()

                # Use y_lstm_test for evaluation
                y_test_for_eval = y_lstm_test

            else:
                continue

            # Evaluate model
            if model_name != "lstm":
                y_test_for_eval = y_test

            model_metrics = evaluate_model(y_test_for_eval, predictions)
            metrics[model_name] = model_metrics
            trained_models[model_name] = model

            # Save model and scalers
            save_model(model, X_scaler, y_scaler, ticker, model_name)

        except Exception as e:
            print(f"Error training {model_name} for {ticker}: {e}")
            continue

    return list(trained_models.keys()), metrics


def save_model(model, X_scaler, y_scaler, ticker: str, model_name: str):
    """
    Save trained model and scalers to disk.

    Args:
        model: Trained model object
        X_scaler: Scaler for features
        y_scaler: Scaler for target
        ticker: Stock ticker
        model_name: Name of the model
    """
    os.makedirs("saved_models", exist_ok=True)

    if model_name == "lstm":
        model_path = f"saved_models/{ticker}_{model_name}.h5"
        X_scaler_path = f"saved_models/{ticker}_{model_name}_X_scaler.pkl"
        y_scaler_path = f"saved_models/{ticker}_{model_name}_y_scaler.pkl"
        try:
            save_lstm_model(model, model_path)
            with open(X_scaler_path, 'wb') as f:
                pickle.dump(X_scaler, f)
            with open(y_scaler_path, 'wb') as f:
                pickle.dump(y_scaler, f)
            print(f"LSTM model and scalers saved: {model_path}, {X_scaler_path}, {y_scaler_path}")
        except Exception as e:
            print(f"Error saving LSTM model {model_name} for {ticker}: {e}")
    else:
        model_path = f"saved_models/{ticker}_{model_name}.pkl"
        X_scaler_path = f"saved_models/{ticker}_{model_name}_X_scaler.pkl"
        y_scaler_path = f"saved_models/{ticker}_{model_name}_y_scaler.pkl"
        try:
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            with open(X_scaler_path, 'wb') as f:
                pickle.dump(X_scaler, f)
            with open(y_scaler_path, 'wb') as f:
                pickle.dump(y_scaler, f)
            print(f"Model and scalers saved: {model_path}, {X_scaler_path}, {y_scaler_path}")
        except Exception as e:
            print(f"Error saving model {model_name} for {ticker}: {e}")


def load_model(ticker: str, model_name: str):
    """
    Load trained model and scalers from disk.

    Args:
        ticker: Stock ticker
        model_name: Name of the model

    Returns:
        Tuple of (model, X_scaler, y_scaler) or (None, None, None) if not found
    """
    if model_name == "lstm":
        model_path = f"saved_models/{ticker}_{model_name}.h5"
        X_scaler_path = f"saved_models/{ticker}_{model_name}_X_scaler.pkl"
        y_scaler_path = f"saved_models/{ticker}_{model_name}_y_scaler.pkl"
        if not (os.path.exists(X_scaler_path) and os.path.exists(y_scaler_path)):
            for alt in ["linear", "rf", "xgb"]:
                alt_x = f"saved_models/{ticker}_{alt}_X_scaler.pkl"
                alt_y = f"saved_models/{ticker}_{alt}_y_scaler.pkl"
                if os.path.exists(alt_x) and os.path.exists(alt_y):
                    X_scaler_path = alt_x
                    y_scaler_path = alt_y
                    break
        if os.path.exists(model_path) and os.path.exists(X_scaler_path) and os.path.exists(y_scaler_path):
            try:
                model = load_lstm_model(model_path)
                with open(X_scaler_path, 'rb') as f:
                    X_scaler = pickle.load(f)
                with open(y_scaler_path, 'rb') as f:
                    y_scaler = pickle.load(f)
                return model, X_scaler, y_scaler
            except Exception as e:
                print(f"Error loading LSTM model {model_name} for {ticker}: {e}")
        return None, None, None

    model_path = f"saved_models/{ticker}_{model_name}.pkl"
    X_scaler_path = f"saved_models/{ticker}_{model_name}_X_scaler.pkl"
    y_scaler_path = f"saved_models/{ticker}_{model_name}_y_scaler.pkl"
    if not (os.path.exists(X_scaler_path) and os.path.exists(y_scaler_path)):
        for alt in ["linear", "rf", "xgb"]:
            alt_x = f"saved_models/{ticker}_{alt}_X_scaler.pkl"
            alt_y = f"saved_models/{ticker}_{alt}_y_scaler.pkl"
            if os.path.exists(alt_x) and os.path.exists(alt_y):
                X_scaler_path = alt_x
                y_scaler_path = alt_y
                break

    if os.path.exists(model_path) and os.path.exists(X_scaler_path) and os.path.exists(y_scaler_path):
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            with open(X_scaler_path, 'rb') as f:
                X_scaler = pickle.load(f)
            with open(y_scaler_path, 'rb') as f:
                y_scaler = pickle.load(f)
            return model, X_scaler, y_scaler
        except Exception as e:
            print(f"Error loading model {model_name} for {ticker}: {e}")

    return None, None, None