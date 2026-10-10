from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict
from datetime import datetime

class ModelMetrics(BaseModel):
    rmse: float
    mae: float
    r2_score: float
    mape: float

class ModelComparison(BaseModel):
    model_name: str
    metrics: ModelMetrics
    best_model: bool = False
    
    model_config = ConfigDict(protected_namespaces=())

class PredictionRequest(BaseModel):
    ticker: Optional[str] = None
    model_name: str
    days_ahead: int = 7
    
    model_config = ConfigDict(protected_namespaces=())

class PredictionResponse(BaseModel):
    ticker: str
    model_name: str
    predicted_price: float
    prediction_date: datetime
    days_ahead: int
    confidence_interval: Optional[Dict[str, float]] = None
    
    model_config = ConfigDict(protected_namespaces=())

class TrainRequest(BaseModel):
    ticker: str
    models: List[str] = ["linear", "rf", "xgb", "lstm"]

class TrainResponse(BaseModel):
    ticker: str
    trained_models: List[str]
    best_model: str
    metrics: Dict[str, ModelMetrics]

class PredictionHistory(BaseModel):
    id: int
    user_id: int
    ticker: str
    model_name: str
    predicted_price: float
    prediction_date: datetime
    days_ahead: int
    actual_price: Optional[float]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())