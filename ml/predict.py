import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from ml.data_loader import load_stock_data
from ml.preprocessing import preprocess_data, prepare_lstm_data
from ml.feature_engineering import engineer_features
from ml.train import load_model
import warnings
warnings.filterwarnings('ignore')

_model_cache = {}
_model_mtime = {}

def load_model_cached(ticker: str, model_name: str):
    """Load a model and its scalers from disk with in-memory caching."""
    cache_key = f"{ticker}_{model_name}"
    model_path = Path(f"saved_models/{ticker}_{model_name}.pkl")
    if model_name == "lstm":
        model_path = Path(f"saved_models/{ticker}_{model_name}.h5")

    current_mtime = model_path.stat().st_mtime if model_path.exists() else None
    if cache_key in _model_cache and _model_mtime.get(cache_key) == current_mtime:
        return _model_cache[cache_key]

    model_tuple = load_model(ticker, model_name)
    if model_tuple is None or model_tuple[0] is None:
        return model_tuple

    _model_cache[cache_key] = model_tuple
    _model_mtime[cache_key] = current_mtime
    return model_tuple

def _get_feature_array(df_subset: pd.DataFrame, X_scaler) -> np.ndarray:
    """Extract features matching the scaler's expected features."""
    if hasattr(X_scaler, 'feature_names_in_') and X_scaler.feature_names_in_ is not None:
        return df_subset.reindex(columns=X_scaler.feature_names_in_, fill_value=0.0).values
    feature_columns = [col for col in df_subset.columns
                      if col not in ['Close', 'Date'] and not col.startswith('Date')]
    return df_subset[feature_columns].values

def make_prediction(ticker: str, model_name: str, days_ahead: int = 7) -> float:
    """
    Make stock price prediction using trained model.

    Args:
        ticker: Stock ticker symbol
        model_name: Name of the trained model
        days_ahead: Number of days to predict ahead

    Returns:
        Predicted price
    """
    # Load model and scalers
    model, X_scaler, y_scaler = load_model_cached(ticker, model_name)
    if model is None:
        raise ValueError(f"Model {model_name} for {ticker} not found")

    # Use cached data and features for better performance
    from app.services.prediction_service import PredictionService
    df_features = PredictionService._get_cached_features(ticker)

    if len(df_features) < 30:
        raise ValueError("Insufficient data for prediction")

    # Get the most recent data point
    latest_data = df_features.iloc[-1:]

    if model_name in ["linear", "rf", "xgb"]:
        # For traditional ML models
        X_input = _get_feature_array(latest_data, X_scaler)
        X_scaled = X_scaler.transform(X_input)
        
        # Make prediction
        prediction_scaled = model.predict(X_scaled)
        
        # Inverse transform the prediction to get actual price
        prediction_actual = y_scaler.inverse_transform(prediction_scaled.reshape(-1, 1))
        
        return float(prediction_actual[0][0])

    elif model_name == "lstm":
        # For LSTM, we need sequence data (60 time steps)
        if len(df_features) < 60:
            raise ValueError("Insufficient data for LSTM prediction (need at least 60 rows)")

        recent_data = _get_feature_array(df_features.iloc[-60:], X_scaler)
        X_scaled = X_scaler.transform(recent_data)
        X_sequence = X_scaled.reshape(1, 60, X_scaled.shape[1])

        prediction_scaled = model.predict(X_sequence, verbose=0)[0][0]
        prediction_actual = y_scaler.inverse_transform([[prediction_scaled]])
        return float(prediction_actual[0][0])

    else:
        raise ValueError(f"Unsupported model type: {model_name}")


def predict_future_sequence(ticker: str, model_name: str, num_days: int = 30) -> list:
    """
    Make sequential multi-day predictions.
    """
    try:
        model, X_scaler, y_scaler = load_model_cached(ticker, model_name)
        if model is None:
            raise ValueError(f"Model {model_name} for {ticker} not found")

        # Load recent data
        df = load_stock_data(ticker, period="6mo")
        if df is None or df.empty:
            raise ValueError(f"No data available for {ticker}")

        df_features = engineer_features(df)
        if len(df_features) < 60:
            raise ValueError("Insufficient data for prediction")

        feature_columns = [col for col in df_features.columns
                          if col not in ['Close', 'Date'] and not col.startswith('Date')]

        predictions = []

        for day in range(num_days):
            try:
                if model_name == "lstm":
                    if len(df_features) < 60:
                        break
                    recent_data = _get_feature_array(df_features.iloc[-60:], X_scaler)
                    X_scaled = X_scaler.transform(recent_data)
                    X_sequence = X_scaled.reshape(1, 60, X_scaled.shape[1])
                    pred_scaled = model.predict(X_sequence, verbose=0)[0][0]
                    pred = float(y_scaler.inverse_transform([[pred_scaled]])[0][0])
                else:
                    latest_row = _get_feature_array(df_features.iloc[-1:], X_scaler)
                    X_scaled = X_scaler.transform(latest_row)
                    pred_scaled = model.predict(X_scaled)
                    pred = float(y_scaler.inverse_transform(pred_scaled.reshape(-1, 1))[0][0])

                predictions.append(pred)

                # Append a synthetic next row for recursive prediction
                next_row = df_features.iloc[-1:].copy()
                if 'Close' in next_row.columns:
                    next_row = next_row.copy()
                    next_row.iloc[0, next_row.columns.get_loc('Close')] = pred
                df_features = pd.concat([df_features, next_row], ignore_index=True)

            except Exception as e:
                print(f"Error at day {day}: {e}")
                break

        return predictions

    except Exception as e:
        raise ValueError(f"Error in future sequence prediction: {e}")

def predict_multiple_days(ticker: str, model_name: str, days: list = [7, 15, 30]) -> dict:
    """
    Make predictions for multiple time horizons.

    Args:
        ticker: Stock ticker
        model_name: Model name
        days: List of days ahead to predict

    Returns:
        Dictionary with predictions
    """
    predictions = {}
    
    # Use sequential prediction for better multi-day forecasting
    try:
        max_days = max(days) if days else 30
        sequence = predict_future_sequence(ticker, model_name, max_days)
        
        for day_idx in days:
            if day_idx - 1 < len(sequence):
                predictions[day_idx] = {
                    "price": sequence[day_idx - 1],
                    "method": "sequential"
                }
            else:
                predictions[day_idx] = None
    except Exception as e:
        print(f"Sequential prediction failed: {e}")
        # Fallback to individual predictions
        for day in days:
            try:
                pred = make_prediction(ticker, model_name, day)
                predictions[day] = {
                    "price": pred,
                    "method": "single"
                }
            except Exception as e:
                print(f"Error predicting {day} days ahead: {e}")
                predictions[day] = None

    return predictions


def get_prediction_confidence(ticker: str, model_name: str, days_ahead: int = 7) -> dict:
    """
    Get prediction with confidence intervals using ensemble methods.

    Args:
        ticker: Stock ticker
        model_name: Model name
        days_ahead: Days ahead to predict

    Returns:
        Dictionary with prediction and confidence intervals
    """
    try:
        prediction = make_prediction(ticker, model_name, days_ahead)

        # Calculate historical volatility for better confidence intervals
        df = load_stock_data(ticker, period="1y")
        if df is not None and not df.empty and 'Close' in df.columns:
            returns = df['Close'].pct_change().dropna()
            volatility = returns.std()
            
            # Confidence interval based on volatility and days ahead
            confidence_range = prediction * volatility * np.sqrt(days_ahead / 252)
        else:
            # Fallback confidence range
            confidence_range = prediction * 0.05

        return {
            "prediction": prediction,
            "lower_bound": prediction - confidence_range,
            "upper_bound": prediction + confidence_range,
            "confidence_level": 0.95,
            "confidence_range": float(confidence_range),
            "volatility_based": df is not None and not df.empty
        }

    except Exception as e:
        raise ValueError(f"Error getting prediction confidence: {e}")


def predict_with_ensemble(ticker: str, models: list = None, days_ahead: int = 7) -> dict:
    """
    Make prediction using ensemble of multiple models.

    Args:
        ticker: Stock ticker symbol
        models: List of model names to use
        days_ahead: Number of days ahead to predict

    Returns:
        Dictionary with ensemble prediction and individual model predictions
    """
    if models is None:
        models = ["linear", "rf", "xgb", "lstm"]

    predictions = []
    model_results = {}

    for model_name in models:
        try:
            pred = make_prediction(ticker, model_name, days_ahead)
            predictions.append(pred)
            model_results[model_name] = {
                "price": pred,
                "weight": 1.0 / len(models)
            }
        except Exception as e:
            print(f"Error with model {model_name}: {e}")
            model_results[model_name] = {"error": str(e)}

    if not predictions:
        raise ValueError("No valid predictions from any model")

    # Calculate weighted average
    ensemble_pred = np.mean(predictions)
    ensemble_std = np.std(predictions)

    return {
        "ensemble_prediction": float(ensemble_pred),
        "std_deviation": float(ensemble_std),
        "lower_bound": float(ensemble_pred - ensemble_std),
        "upper_bound": float(ensemble_pred + ensemble_std),
        "model_predictions": model_results,
        "num_models": len([m for m in model_results if "error" not in model_results[m]])
    }


def get_future_price_forecast(ticker: str, model_name: str, days: int = 30, 
                             return_dataframe: bool = False) -> dict:
    """
    Get complete future price forecast with dates and confidence levels.

    Args:
        ticker: Stock ticker symbol
        model_name: Model name
        days: Number of days to forecast
        return_dataframe: Whether to return as DataFrame

    Returns:
        Dictionary or DataFrame with forecast data
    """
    try:
        # Get predictions
        predictions = predict_future_sequence(ticker, model_name, days)
        
        if not predictions:
            raise ValueError("Could not generate predictions")

        # Get current price
        df = load_stock_data(ticker, period="1d")
        current_price = df['Close'].iloc[-1] if df is not None and not df.empty else None

        # Generate dates
        start_date = datetime.now().date()
        dates = [start_date + timedelta(days=i) for i in range(1, len(predictions) + 1)]

        # Create forecast data
        forecast_data = []
        volatility = 0.02  # Default 2% daily volatility

        for i, (date, pred) in enumerate(zip(dates, predictions)):
            days_ahead = i + 1
            # Uncertainty increases with time horizon
            uncertainty = volatility * np.sqrt(days_ahead)
            
            forecast_data.append({
                "date": date,
                "predicted_price": pred,
                "days_ahead": days_ahead,
                "lower_bound": pred * (1 - uncertainty),
                "upper_bound": pred * (1 + uncertainty),
                "confidence": 0.95 if days_ahead <= 15 else 0.90 if days_ahead <= 30 else 0.85
            })

        if return_dataframe:
            return pd.DataFrame(forecast_data)
        else:
            return {
                "ticker": ticker,
                "current_price": current_price,
                "forecast": forecast_data,
                "start_date": str(start_date),
                "end_date": str(dates[-1]) if dates else None,
                "model": model_name
            }

    except Exception as e:
        raise ValueError(f"Error generating forecast: {e}")