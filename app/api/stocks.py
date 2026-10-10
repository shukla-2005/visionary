from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from app.schemas.stock import (
    StockInfo, HistoricalData, TechnicalIndicators, StockAnalysis,
    ComparisonRequest, ComparisonResponse, TopMovers, SectorAnalysis
)
from app.services.stock_service import StockService

router = APIRouter()

@router.get("/search/{ticker}", response_model=StockInfo)
async def search_stock(ticker: str):
    stock_info = StockService.get_stock_info(ticker)
    if not stock_info:
        raise HTTPException(
            status_code=404,
            detail=f"Stock {ticker} not found or temporarily unavailable. Please verify the ticker symbol and try again."
        )
    return stock_info

@router.get("/ticker-search")
async def ticker_search(q: str = Query(..., description="Company name or ticker symbol to search")):
    """
    Search for ticker symbols by company name or partial ticker.
    Powered by Alpha Vantage SYMBOL_SEARCH — returns up to 10 best matches.
    """
    if not q or len(q.strip()) < 1:
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required.")
    results = StockService.search_tickers(q.strip())
    return {"query": q, "results": results}

@router.get("/listed")
async def get_listed_stocks(state: str = Query("active", description="'active' or 'delisted'")):
    """
    Return the full list of stocks listed on US exchanges (NYSE, NASDAQ, etc.)
    sourced from Alpha Vantage LISTING_STATUS endpoint.
    """
    stocks = StockService.get_listed_stocks(state=state)
    return {"state": state, "count": len(stocks), "stocks": stocks}

@router.get("/history/{ticker}", response_model=List[HistoricalData])
async def get_stock_history(ticker: str, period: str = "1y"):
    historical_data = StockService.get_historical_data(ticker, period)
    if not historical_data:
        raise HTTPException(
            status_code=404,
            detail=f"Historical data for {ticker} not available or temporarily unavailable. This may be due to rate limiting. Please try again in a few minutes."
        )
    return historical_data

@router.get("/indicators/{ticker}", response_model=List[TechnicalIndicators])
async def get_technical_indicators(ticker: str, period: str = "1y"):
    indicators = StockService.get_technical_indicators(ticker, period)
    if not indicators:
        raise HTTPException(status_code=404, detail="Technical indicators not available")
    return indicators

@router.get("/analysis/{ticker}", response_model=StockAnalysis)
async def get_stock_analysis(ticker: str, period: str = "1y"):
    stock_info = StockService.get_stock_info(ticker)
    historical_data = StockService.get_historical_data(ticker, period)
    indicators = StockService.get_technical_indicators(ticker, period)

    if not stock_info or not historical_data:
        raise HTTPException(status_code=404, detail="Stock analysis not available")

    return StockAnalysis(
        ticker=ticker,
        info=stock_info,
        historical_data=historical_data,
        indicators=indicators
    )

@router.post("/compare", response_model=ComparisonResponse)
async def compare_stocks(request: ComparisonRequest):
    if len(request.tickers) < 2 or len(request.tickers) > 5:
        raise HTTPException(status_code=400, detail="Compare 2-5 stocks at a time")

    comparison_data = StockService.compare_stocks(request.tickers, request.period)
    return ComparisonResponse(
        tickers=request.tickers,
        data=comparison_data
    )

@router.get("/top-movers", response_model=TopMovers)
async def get_top_movers():
    return StockService.get_top_movers()

@router.get("/sector-analysis", response_model=List[SectorAnalysis])
async def get_sector_analysis():
    return StockService.get_sector_analysis()