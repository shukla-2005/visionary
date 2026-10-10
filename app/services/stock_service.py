"""
Stock service — uses yfinance 1.3.0 as primary data source.
Alpha Vantage is used only for ticker search (SYMBOL_SEARCH) and
full market listing (LISTING_STATUS), which are free-tier endpoints.
"""

import requests as http_requests
import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import time
import os
import csv
import io
import datetime

from ml.indicators import calculate_technical_indicators
from app.schemas.stock import StockInfo, HistoricalData, TechnicalIndicators

# ---------------------------------------------------------------------------
# Alpha Vantage — only for search / listing (free endpoints)
# ---------------------------------------------------------------------------
AV_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
AV_BASE_URL = "https://www.alphavantage.co/query"

# period string → number of trading days
PERIOD_TO_DAYS = {
    "1d": 1, "5d": 5, "1mo": 21, "3mo": 63,
    "6mo": 126, "1y": 252, "2y": 504, "5y": 1260, "max": 9999,
}


class StockService:
    _cache: Dict = {}
    _cache_timeout = 300  # 5 minutes

    # ------------------------------------------------------------------
    # Cache helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _cached(key: str):
        if key in StockService._cache:
            data, ts = StockService._cache[key]
            if time.time() - ts < StockService._cache_timeout:
                return data
        return None

    @staticmethod
    def _store(key: str, value):
        StockService._cache[key] = (value, time.time())

    # ------------------------------------------------------------------
    # Alpha Vantage helpers (search / listing only)
    # ------------------------------------------------------------------
    @staticmethod
    def _av_get(params: dict) -> dict:
        params["apikey"] = AV_API_KEY
        try:
            resp = http_requests.get(AV_BASE_URL, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            if "Note" in data or "Information" in data:
                raise RuntimeError(data.get("Note") or data.get("Information", "rate limited"))
            return data
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"AV request failed: {e}")

    # ------------------------------------------------------------------
    # Ticker search (Alpha Vantage SYMBOL_SEARCH — free)
    # ------------------------------------------------------------------
    @staticmethod
    def search_tickers(query: str) -> List[dict]:
        cache_key = f"search_{query.lower()}"
        cached = StockService._cached(cache_key)
        if cached is not None:
            return cached
        try:
            data = StockService._av_get({"function": "SYMBOL_SEARCH", "keywords": query})
            results = [
                {
                    "symbol": m.get("1. symbol", ""),
                    "name": m.get("2. name", ""),
                    "type": m.get("3. type", ""),
                    "region": m.get("4. region", ""),
                    "currency": m.get("8. currency", ""),
                }
                for m in data.get("bestMatches", [])
            ]
            StockService._store(cache_key, results)
            return results
        except Exception as e:
            print(f"Ticker search error for '{query}': {e}")
            return []

    # ------------------------------------------------------------------
    # Full market listing (Alpha Vantage LISTING_STATUS — free)
    # ------------------------------------------------------------------
    @staticmethod
    def get_listed_stocks(state: str = "active") -> List[dict]:
        cache_key = f"listing_{state}"
        cached = StockService._cached(cache_key)
        if cached is not None:
            return cached
        try:
            url = f"{AV_BASE_URL}?function=LISTING_STATUS&state={state}&apikey={AV_API_KEY}"
            resp = http_requests.get(url, timeout=30)
            resp.raise_for_status()
            reader = csv.DictReader(io.StringIO(resp.text))
            stocks = [row for row in reader]
            StockService._store(cache_key, stocks)
            return stocks
        except Exception as e:
            print(f"Error fetching listing status: {e}")
            return []

    # ------------------------------------------------------------------
    # Stock info — yfinance fast_info + history
    # ------------------------------------------------------------------
    @staticmethod
    def get_stock_info(ticker: str) -> Optional[StockInfo]:
        cache_key = f"info_{ticker.upper()}"
        cached = StockService._cached(cache_key)
        if cached is not None:
            return cached

        try:
            t = yf.Ticker(ticker)
            fi = t.fast_info

            last_price = fi.last_price
            if last_price is None or (isinstance(last_price, float) and np.isnan(last_price)):
                print(f"No price data for {ticker}")
                return None

            # Get name and sector from info (cached by yfinance internally)
            name = ticker.upper()
            sector = None
            market_cap = None
            try:
                info = t.info
                name = info.get("longName") or info.get("shortName") or ticker.upper()
                sector = info.get("sector")
                market_cap = info.get("marketCap") or fi.market_cap
            except Exception:
                market_cap = fi.market_cap

            year_high = fi.year_high
            year_low = fi.year_low
            avg_vol = fi.three_month_average_volume

            stock_info = StockInfo(
                ticker=ticker.upper(),
                name=name,
                sector=sector,
                market_cap=float(market_cap) if market_cap else None,
                current_price=float(last_price),
                week_52_high=float(year_high) if year_high else None,
                week_52_low=float(year_low) if year_low else None,
                average_volume=float(avg_vol) if avg_vol else None,
            )
            StockService._store(cache_key, stock_info)
            return stock_info

        except Exception as e:
            print(f"Error fetching stock info for {ticker}: {e}")
            return None

    # ------------------------------------------------------------------
    # Historical data — yfinance history()
    # ------------------------------------------------------------------
    @staticmethod
    def get_historical_data(ticker: str, period: str = "1y") -> List[HistoricalData]:
        cache_key = f"history_{ticker.upper()}_{period}"
        cached = StockService._cached(cache_key)
        if cached is not None:
            return cached

        try:
            t = yf.Ticker(ticker)
            hist = t.history(period=period, auto_adjust=True)

            if hist.empty:
                print(f"No historical data for {ticker}")
                return []

            historical_data: List[HistoricalData] = []
            for date, row in hist.iterrows():
                # date is timezone-aware; strip tz for JSON serialisation
                dt = date.to_pydatetime().replace(tzinfo=None)
                historical_data.append(
                    HistoricalData(
                        date=dt,
                        open=float(row["Open"]),
                        high=float(row["High"]),
                        low=float(row["Low"]),
                        close=float(row["Close"]),
                        volume=int(row["Volume"]),
                        adj_close=float(row["Close"]),  # auto_adjust=True already adjusts
                    )
                )

            StockService._store(cache_key, historical_data)
            return historical_data

        except Exception as e:
            print(f"Error fetching historical data for {ticker}: {e}")
            return []

    # ------------------------------------------------------------------
    # Technical indicators
    # ------------------------------------------------------------------
    @staticmethod
    def get_technical_indicators(ticker: str, period: str = "1y") -> List[TechnicalIndicators]:
        try:
            hist_data = StockService.get_historical_data(ticker, period)
            if not hist_data:
                return []

            df = pd.DataFrame([
                {"Close": p.close, "High": p.high, "Low": p.low, "Volume": p.volume}
                for p in hist_data
            ])
            indicators_df = calculate_technical_indicators(df)

            indicators = []
            for _, row in indicators_df.iterrows():
                if not pd.isna(row.get("SMA_20")) or not pd.isna(row.get("RSI")) or not pd.isna(row.get("MACD")):
                    def _v(k):
                        v = row.get(k)
                        return None if v is None or pd.isna(v) else float(v)
                    indicators.append(TechnicalIndicators(
                        sma_20=_v("SMA_20"), sma_50=_v("SMA_50"),
                        ema_12=_v("EMA_12"), ema_26=_v("EMA_26"),
                        rsi=_v("RSI"), macd=_v("MACD"),
                        macd_signal=_v("MACD_Signal"), macd_hist=_v("MACD_Hist"),
                        bb_upper=_v("BB_Upper"), bb_middle=_v("BB_Middle"),
                        bb_lower=_v("BB_Lower"), momentum=_v("Momentum"),
                    ))
            return indicators
        except Exception as e:
            print(f"Error calculating indicators for {ticker}: {e}")
            return []

    # ------------------------------------------------------------------
    # Compare stocks
    # ------------------------------------------------------------------
    @staticmethod
    def compare_stocks(tickers: List[str], period: str = "1y") -> Dict[str, List[HistoricalData]]:
        return {ticker: StockService.get_historical_data(ticker, period) for ticker in tickers}

    # ------------------------------------------------------------------
    # Top movers — yfinance batch download
    # ------------------------------------------------------------------
    @staticmethod
    def get_top_movers():
        cache_key = "top_movers"
        cached = StockService._cached(cache_key)
        if cached is not None:
            return cached

        major_stocks = [
            # US Mega-cap
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
            # US Tech
            "NFLX", "ADBE", "CRM", "INTC", "AMD", "ORCL", "CSCO", "IBM", "QCOM",
            "AVGO", "TXN", "MU", "PANW", "CRWD", "SNOW", "DDOG", "ZS", "NET",
            # Semiconductors
            "TSM", "ASML", "ARM", "SMCI",
            # Chinese ADRs
            "BABA", "JD", "NIO", "BIDU", "PDD",
            # Fintech / Payments
            "PYPL", "XYZ", "V", "MA", "AXP", "COIN", "HOOD",
            # Social / Media
            "SPOT", "ROKU", "SNAP", "PINS", "RBLX",
            # Mobility / SaaS
            "UBER", "LYFT", "ZM", "SHOP", "EBAY",
            # Financials
            "JPM", "BAC", "WFC", "GS", "MS", "C", "BLK",
            # Healthcare
            "JNJ", "PFE", "MRNA", "ABBV", "LLY", "UNH", "AMGN",
            # Energy
            "XOM", "CVX", "COP",
            # Consumer
            "WMT", "TGT", "COST", "HD", "NKE", "SBUX", "MCD", "DIS",
            # Industrials
            "BA", "CAT", "GE", "HON",
        ]

        movers = []
        try:
            # Batch download is much faster than individual calls
            tickers_str = " ".join(major_stocks)
            data = yf.download(
                tickers_str,
                period="5d",
                interval="1d",
                auto_adjust=True,
                progress=False,
                threads=True,
            )

            close = data["Close"] if "Close" in data else data.get("close", pd.DataFrame())
            if close.empty:
                raise ValueError("Empty batch download")

            for ticker in major_stocks:
                try:
                    if ticker not in close.columns:
                        continue
                    prices = close[ticker].dropna()
                    if len(prices) < 2:
                        continue
                    current_price = float(prices.iloc[-1])
                    prev_price = float(prices.iloc[-2])
                    change_pct = ((current_price - prev_price) / prev_price) * 100
                    movers.append({
                        "ticker": ticker,
                        "name": ticker,
                        "current_price": round(current_price, 2),
                        "change_percent": round(change_pct, 2),
                    })
                except Exception:
                    continue

        except Exception as e:
            print(f"Batch download failed: {e}. Falling back to individual fetches.")
            for ticker in major_stocks[:20]:  # limit fallback to avoid rate limits
                try:
                    t = yf.Ticker(ticker)
                    hist = t.history(period="5d", auto_adjust=True)
                    if len(hist) >= 2:
                        current_price = float(hist["Close"].iloc[-1])
                        prev_price = float(hist["Close"].iloc[-2])
                        change_pct = ((current_price - prev_price) / prev_price) * 100
                        movers.append({
                            "ticker": ticker,
                            "name": ticker,
                            "current_price": round(current_price, 2),
                            "change_percent": round(change_pct, 2),
                        })
                except Exception:
                    continue

        gainers = sorted([m for m in movers if m["change_percent"] > 0],
                         key=lambda x: x["change_percent"], reverse=True)[:10]
        losers = sorted([m for m in movers if m["change_percent"] < 0],
                        key=lambda x: x["change_percent"])[:10]

        result = {"gainers": gainers, "losers": losers, "all_stocks": movers}
        StockService._store(cache_key, result)
        return result

    # ------------------------------------------------------------------
    # Sector analysis
    # ------------------------------------------------------------------
    @staticmethod
    def get_sector_analysis():
        cache_key = "sector_analysis"
        cached = StockService._cached(cache_key)
        if cached is not None:
            return cached

        sectors = {
            "Technology":           ["AAPL", "MSFT", "NVDA", "INTC", "AMD"],
            "Communication":        ["GOOGL", "META", "NFLX", "DIS", "SNAP"],
            "Consumer Discretionary": ["AMZN", "TSLA", "HD", "NKE", "MCD"],
            "Financials":           ["JPM", "BAC", "WFC", "GS", "MS"],
            "Healthcare":           ["JNJ", "PFE", "UNH", "ABBV", "LLY"],
            "Energy":               ["XOM", "CVX", "COP", "SLB", "EOG"],
            "Consumer Staples":     ["WMT", "COST", "PG", "KO", "PEP"],
            "Industrials":          ["BA", "CAT", "GE", "HON", "MMM"],
        }

        # Batch download 1-month data for all sector tickers
        all_tickers = [t for tickers in sectors.values() for t in tickers]
        try:
            data = yf.download(
                " ".join(all_tickers),
                period="1mo",
                interval="1d",
                auto_adjust=True,
                progress=False,
                threads=True,
            )
            close = data["Close"] if "Close" in data else pd.DataFrame()
        except Exception as e:
            print(f"Sector batch download failed: {e}")
            close = pd.DataFrame()

        sector_data = []
        for sector_name, tickers in sectors.items():
            sector_stocks = []
            total_perf = 0.0
            count = 0

            for ticker in tickers:
                info = StockService.get_stock_info(ticker)
                if info:
                    sector_stocks.append(info)

                # Calculate performance from batch data
                try:
                    if not close.empty and ticker in close.columns:
                        prices = close[ticker].dropna()
                        if len(prices) >= 2:
                            perf = ((float(prices.iloc[-1]) - float(prices.iloc[0])) / float(prices.iloc[0])) * 100
                            total_perf += perf
                            count += 1
                except Exception:
                    continue

            if sector_stocks:
                sector_data.append({
                    "sector": sector_name,
                    "stocks": sector_stocks,
                    "average_performance": round(total_perf / count, 2) if count > 0 else 0.0,
                })

        StockService._store(cache_key, sector_data)
        return sector_data
