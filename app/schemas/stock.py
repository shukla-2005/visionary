from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class StockInfo(BaseModel):
    ticker: str
    name: str
    sector: Optional[str] = None
    market_cap: Optional[float] = None
    current_price: float = 0.0
    week_52_high: Optional[float] = None
    week_52_low: Optional[float] = None
    average_volume: Optional[float] = None

class HistoricalData(BaseModel):
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    adj_close: Optional[float] = None

class TechnicalIndicators(BaseModel):
    sma_20: Optional[float]
    sma_50: Optional[float]
    ema_12: Optional[float]
    ema_26: Optional[float]
    rsi: Optional[float]
    macd: Optional[float]
    macd_signal: Optional[float]
    macd_hist: Optional[float]
    bb_upper: Optional[float]
    bb_middle: Optional[float]
    bb_lower: Optional[float]
    momentum: Optional[float]

class StockAnalysis(BaseModel):
    ticker: str
    info: StockInfo
    historical_data: List[HistoricalData]
    indicators: List[TechnicalIndicators]

class ComparisonRequest(BaseModel):
    tickers: List[str]
    period: str = "1y"

class ComparisonResponse(BaseModel):
    tickers: List[str]
    data: Dict[str, List[HistoricalData]]

class SectorAnalysis(BaseModel):
    sector: str
    stocks: List[StockInfo]
    average_performance: float

class TopMovers(BaseModel):
    gainers: List[Dict[str, Any]]
    losers: List[Dict[str, Any]]
    all_stocks: List[Dict[str, Any]] = []

class StockScreenerRequest(BaseModel):
    market_cap_min: Optional[float] = None
    market_cap_max: Optional[float] = None
    volume_min: Optional[int] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    volatility_min: Optional[float] = None
    sector: Optional[str] = None

class StockScreenerResponse(BaseModel):
    stocks: List[StockInfo]