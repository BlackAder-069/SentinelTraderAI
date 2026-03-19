import os
from dotenv import load_dotenv

load_dotenv()

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

DEFAULT_SYMBOL = os.getenv("DEFAULT_SYMBOL", "SPY")
DEFAULT_TIMEFRAME = os.getenv("DEFAULT_TIMEFRAME", "1d")

RISK_MAX_DRAWDOWN = float(os.getenv("RISK_MAX_DRAWDOWN", "0.05"))
RISK_BASE_ORDER_SIZE = float(os.getenv("RISK_BASE_ORDER_SIZE", "0.01"))
