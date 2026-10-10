from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, stocks, models, history, reports
from app.core.config import settings
from app.db.database import Base, engine
from app.models import user, prediction_history
import os

# Create database tables
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: preload key data so the first prediction request is faster
    try:
        from app.services.prediction_service import PredictionService
        PredictionService._get_cached_data("AAPL")
        PredictionService._get_cached_features("AAPL")
    except Exception:
        pass
    yield


app = FastAPI(
    title="Stock Market Analysis API",
    description="API for stock analysis and prediction",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all origins so Streamlit on Render can reach FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(stocks.router, prefix="/stocks", tags=["Stocks"])
app.include_router(models.router, prefix="/models", tags=["Models"])
app.include_router(history.router, prefix="/history", tags=["History"])
app.include_router(reports.router, prefix="/report", tags=["Reports"])

@app.get("/")
async def root():
    return {"message": "Stock Market Analysis API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
