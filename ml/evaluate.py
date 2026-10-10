import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def evaluate_model(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """
    Evaluate model performance with multiple metrics.

    Args:
        y_true: True values
        y_pred: Predicted values

    Returns:
        Dictionary with evaluation metrics
    """
    # Convert to numpy arrays if needed
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    # Calculate metrics
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    # Mean Absolute Percentage Error
    non_zero = y_true != 0
    if np.any(non_zero):
        mape = np.mean(np.abs((y_true[non_zero] - y_pred[non_zero]) / y_true[non_zero])) * 100
    else:
        mape = 0.0

    # Additional metrics
    mse = mean_squared_error(y_true, y_pred)

    return {
        "rmse": float(rmse),
        "mae": float(mae),
        "r2_score": float(r2),
        "mape": float(mape),
        "mse": float(mse)
    }

def calculate_direction_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate directional accuracy (how often the model predicts the correct direction).

    Args:
        y_true: True values
        y_pred: Predicted values

    Returns:
        Directional accuracy as percentage
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    # Calculate direction changes
    true_direction = np.sign(np.diff(y_true))
    pred_direction = np.sign(np.diff(y_pred))

    # Calculate accuracy
    correct_predictions = np.sum(true_direction == pred_direction)
    total_predictions = len(true_direction)

    accuracy = (correct_predictions / total_predictions) * 100

    return float(accuracy)

def evaluate_model_comprehensive(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """
    Comprehensive model evaluation.

    Args:
        y_true: True values
        y_pred: Predicted values

    Returns:
        Dictionary with all evaluation metrics
    """
    basic_metrics = evaluate_model(y_true, y_pred)
    direction_accuracy = calculate_direction_accuracy(y_true, y_pred)

    # Additional metrics
    mean_error = np.mean(y_pred - y_true)
    median_error = np.median(y_pred - y_true)
    std_error = np.std(y_pred - y_true)

    comprehensive_metrics = {
        **basic_metrics,
        "direction_accuracy": direction_accuracy,
        "mean_error": float(mean_error),
        "median_error": float(median_error),
        "std_error": float(std_error)
    }

    return comprehensive_metrics

def compare_models_metrics(models_metrics: dict) -> dict:
    """
    Compare multiple models and find the best one.

    Args:
        models_metrics: Dictionary with model names as keys and metrics as values

    Returns:
        Dictionary with comparison results
    """
    if not models_metrics:
        return {}

    # Find best model for each metric
    best_models = {}
    metrics_list = ["rmse", "mae", "mape", "r2_score"]

    for metric in metrics_list:
        if metric in ["rmse", "mae", "mape"]:
            # Lower is better
            best_model = min(models_metrics.items(), key=lambda x: x[1].get(metric, float('inf')))
        else:
            # Higher is better
            best_model = max(models_metrics.items(), key=lambda x: x[1].get(metric, float('-inf')))

        best_models[metric] = {
            "model": best_model[0],
            "value": best_model[1].get(metric)
        }

    # Overall best model (weighted average of normalized metrics)
    overall_scores = {}
    for model_name, metrics in models_metrics.items():
        # Normalize metrics (lower rmse/mae/mape is better, higher r2 is better)
        rmse_norm = 1 / (1 + metrics.get("rmse", 0))  # Avoid division by zero
        mae_norm = 1 / (1 + metrics.get("mae", 0))
        mape_norm = 1 / (1 + metrics.get("mape", 0))
        r2_norm = metrics.get("r2_score", 0)

        # Weighted score
        overall_score = (rmse_norm * 0.3 + mae_norm * 0.3 + mape_norm * 0.2 + r2_norm * 0.2)
        overall_scores[model_name] = overall_score

    best_overall = max(overall_scores.items(), key=lambda x: x[1])

    return {
        "best_by_metric": best_models,
        "best_overall": {
            "model": best_overall[0],
            "score": best_overall[1]
        },
        "all_scores": overall_scores
    }