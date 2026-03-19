from abc import ABC, abstractmethod
import pandas as pd

class BaseIngestor(ABC):
    @abstractmethod
    def fetch_ohlcv(self, symbol: str, period: str, interval: str) -> pd.DataFrame:
        pass

    @abstractmethod
    def fetch_news(self, symbol:str):
        pass
