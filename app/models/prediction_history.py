from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ticker = Column(String, nullable=False)
    model_name = Column(String, nullable=False)
    predicted_price = Column(Float, nullable=False)
    prediction_date = Column(DateTime, nullable=False)
    days_ahead = Column(Integer, nullable=False)
    actual_price = Column(Float, nullable=True)  # To be updated later if available
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    user = relationship("User")