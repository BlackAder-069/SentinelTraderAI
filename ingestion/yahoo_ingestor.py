import yfinance as yf
import pandas as pd
from .base_ingestor import BaseIngestor

class YahooIngestor(BaseIngestor):
    def fetch_ohlcv(self, symbol: str, period: str="30d", interval: str="1d") -> pd.DataFrame:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        if df is None or df.empty:
            return pd.DataFrame()
        df = df.reset_index()
        return df

    def fetch_news(self, symbol: str):
        # Placeholder; replace with real news API integration
        return []
