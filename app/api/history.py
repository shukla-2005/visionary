from fastapi import APIRouter, Depends
from typing import List
from app.schemas.prediction import PredictionHistory
from app.services.prediction_service import PredictionService
from app.utils.dependencies import get_current_user
from app.models.user import User
from sqlalchemy.orm import Session
from app.db.database import get_db

router = APIRouter()

@router.get("/", response_model=List[PredictionHistory])
async def get_prediction_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return PredictionService.get_prediction_history(db, current_user.id)