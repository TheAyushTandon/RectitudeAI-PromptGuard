"""
Stock Price Tool — simulated market data for the Financial Advisor Agent.

Returns realistic-looking but completely fictional stock prices
from a static dataset. No real market data or API calls.
"""

from __future__ import annotations
import random
from dataclasses import dataclass
from typing import Dict, Optional

from backend.utils.logging import get_logger

logger = get_logger(__name__)

# Static demo stock data
_STOCK_DATA: Dict[str, dict] = {
    "AAPL":  {"name": "Apple Inc.",          "price": 178.50, "change": +1.23, "volume": "52.3M"},
    "GOOGL": {"name": "Alphabet Inc.",       "price": 141.25, "change": -0.87, "volume": "28.1M"},
    "MSFT":  {"name": "Microsoft Corp.",     "price": 415.60, "change": +2.45, "volume": "31.7M"},
    "AMZN":  {"name": "Amazon.com Inc.",     "price": 185.30, "change": +0.56, "volume": "45.2M"},
    "META":  {"name": "Meta Platforms Inc.", "price": 502.40, "change": -1.12, "volume": "18.9M"},
    "TSLA":  {"name": "Tesla Inc.",          "price": 248.75, "change": +3.67, "volume": "67.4M"},
    "NVDA":  {"name": "NVIDIA Corp.",        "price": 875.20, "change": +12.30, "volume": "42.8M"},
    "NFLX":  {"name": "Netflix Inc.",        "price": 628.90, "change": -2.34, "volume": "8.2M"},
    "JPM":   {"name": "JPMorgan Chase",      "price": 198.15, "change": +0.45, "volume": "12.5M"},
    "V":     {"name": "Visa Inc.",           "price": 281.30, "change": +1.02, "volume": "9.1M"},
}


@dataclass
class StockQuote:
    """Stock price quote."""
    symbol: str
    name: str
    price: float
    change: float
    change_pct: float
    volume: str
    market_status: str = "Open (Simulated)"


class StockTool:
    """Simulated stock price lookup tool."""

    def get_quote(self, symbol: str) -> dict:
        """
        Get a simulated stock quote.

        Args:
            symbol: Stock ticker symbol (e.g., "AAPL")

        Returns:
            Dict with stock data or error
        """
        symbol = symbol.upper().strip()

        if symbol not in _STOCK_DATA:
            return {
                "error": f"Unknown ticker: {symbol}",
                "available_tickers": list(_STOCK_DATA.keys()),
            }

        data = _STOCK_DATA[symbol]
        # Add slight randomness for demo realism
        price_jitter = random.uniform(-0.5, 0.5)
        current_price = round(data["price"] + price_jitter, 2)
        change = round(data["change"] + random.uniform(-0.2, 0.2), 2)
        change_pct = round((change / current_price) * 100, 2)

        logger.info("StockTool: %s = $%.2f (%+.2f)", symbol, current_price, change)

        return {
            "symbol": symbol,
            "name": data["name"],
            "price": current_price,
            "change": change,
            "change_pct": change_pct,
            "volume": data["volume"],
            "market_status": "Open (Simulated)",
            "disclaimer": "SIMULATED DATA — Not real market prices",
        }

    def get_all_quotes(self) -> list:
        """Get quotes for all available stocks."""
        return [self.get_quote(sym) for sym in _STOCK_DATA]

    @property
    def available_tickers(self) -> list:
        """List of available ticker symbols."""
        return list(_STOCK_DATA.keys())
