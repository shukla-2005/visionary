from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List
from pydantic import BaseModel, ConfigDict
from app.schemas.prediction import (
    TrainRequest, TrainResponse, PredictionRequest, PredictionResponse,
    ModelComparison
)
from app.services.prediction_service import PredictionService
from app.utils.dependencies import get_current_user
from app.models.user import User
from sqlalchemy.orm import Session
from app.db.database import get_db

# Pydantic models for batch requests
class BatchPredictionRequest(BaseModel):
    tickers: List[str]
    model_name: str = "lstm"
    days_ahead: int = 7

    model_config = ConfigDict(protected_namespaces=())

router = APIRouter()

@router.post("/train/{ticker}", response_model=TrainResponse)
async def train_models(
    ticker: str,
    request: TrainRequest = None,
    current_user: User = Depends(get_current_user)
):
    if request is None:
        request = TrainRequest(ticker=ticker)

    try:
        return PredictionService.train_models_for_ticker(ticker, request.models)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict/{ticker}", response_model=PredictionResponse)
async def make_prediction(
    ticker: str,
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        prediction = PredictionService.make_prediction(
            ticker, request.model_name, request.days_ahead
        )

        # Save to history in background
        background_tasks.add_task(
            PredictionService.save_prediction_history,
            db, current_user.id, prediction
        )

        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compare/{ticker}", response_model=List[ModelComparison])
async def compare_models(ticker: str, current_user: User = Depends(get_current_user)):
    # This would load saved models and compare their metrics
    # For now, return a placeholder
    try:
        # In a real implementation, you'd load metrics from saved models
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ensemble/{ticker}")
async def predict_ensemble(
    ticker: str,
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Make prediction using ensemble of multiple models."""
    try:
        result = PredictionService.make_ensemble_prediction(ticker, request.days_ahead)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/confidence/{ticker}")
async def get_confidence_prediction(
    ticker: str,
    request: PredictionRequest,
    current_user: User = Depends(get_current_user)
):
    """Get prediction with confidence intervals."""
    try:
        result = PredictionService.get_prediction_with_confidence(
            ticker, request.model_name, request.days_ahead
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/forecast/{ticker}")
async def get_forecast(
    ticker: str,
    request: PredictionRequest,
    days: int = 30,
    current_user: User = Depends(get_current_user)
):
    """Get future price forecast with dates and confidence levels."""
    try:
        result = PredictionService.get_future_forecast(ticker, request.model_name, days)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict-batch")
async def predict_multiple_stocks(
    request: BatchPredictionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Make predictions for multiple stocks at once."""
    try:
        results = PredictionService.predict_multiple_stocks(
            request.tickers, request.model_name, request.days_ahead
        )

        # Save predictions to history in background
        for ticker, result in results.items():
            if result.get("success"):
                from datetime import datetime
                pred_resp = PredictionResponse(
                    ticker=ticker,
                    model_name=request.model_name,
                    predicted_price=result["prediction"],
                    prediction_date=datetime.now(),
                    days_ahead=request.days_ahead
                )
                background_tasks.add_task(
                    PredictionService.save_prediction_history,
                    db, current_user.id, pred_resp
                )

        return {
            "tickers": request.tickers,
            "model_name": request.model_name,
            "days_ahead": request.days_ahead,
            "predictions": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))