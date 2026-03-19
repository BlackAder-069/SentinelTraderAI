import yfinance as yf
from .base_ingestor import BaseIngestor


class NewsIngestor(BaseIngestor):
    def fetch_ohlcv(self, symbol: str, period: str, interval: str):
        raise NotImplementedError("Use stock data ingestor for OHLCV")

    def fetch_news(self, symbol: str):
        ticker = yf.Ticker(symbol)
        # yfinance provides a .news list with headline and link
        try:
            raw_news = ticker.news
        except Exception:
            raw_news = []

        out = []
        for item in raw_news[:10]:
            if not isinstance(item, dict):
                continue
            out.append({
                "title": item.get("title", ""),
                "publisher": item.get("publisher", ""),
                "link": item.get("link", ""),
                "providerPublishTime": item.get("providerPublishTime"),
            })
        return out
