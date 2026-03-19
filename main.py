import logging

from ingestion.yahoo_ingestor import YahooIngestor
from ingestion.news_ingestor import NewsIngestor
from ingestion.social_sentiment_ingestor import SocialSentimentIngestor
from signal_processing.technical import (
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_momentum,
    aggregate_signal,
)
from signal_processing.finbert_sentiment import analyze_news_sentiment
from risk.risk_manager import RiskManager
from risk.position_manager import PositionManager
from agent.langchain_agent import TraderAgent
from execution.alpaca_executor import AlpacaExecutor
from config import ALPACA_API_KEY, ALPACA_SECRET_KEY


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


def run_cycle(symbol="SPY", capital=100000.0):
    logging.info("Running full cycle for %s", symbol)

    position_manager = PositionManager()
    current_position = position_manager.get_position()

    price_df = YahooIngestor().fetch_ohlcv(symbol, period="60d", interval="1d")
    if price_df is None or price_df.empty:
        logging.warning("No price data for %s", symbol)
        return

    news = NewsIngestor().fetch_news(symbol)
    social = SocialSentimentIngestor().fetch_social_sentiment(symbol)

    state_price = float(price_df["Close"].dropna().iloc[-1])

    if current_position:
        stop_action = RiskManager().enforce_stop_loss(current_position, state_price)
        if stop_action.get("action") == "sell":
            logging.info("Stop-loss/trailing-stop condition met: %s", stop_action)
            if ALPACA_API_KEY and ALPACA_SECRET_KEY:
                try:
                    instr = {
                        "action": "sell",
                        "symbol": current_position.get("symbol"),
                        "qty": current_position.get("qty", 0),
                    }
                    AlpacaExecutor().execute_order(instr)
                    position_manager.clear_position()
                except Exception as e:
                    logging.error("Stop execution failed: %s", e)
            else:
                logging.warning("Alpaca keys not set; not executing stop order")

    series = price_df["Close"].dropna()
    ema = calculate_ema(series, 12).iloc[-1]
    rsi = calculate_rsi(series, 14).iloc[-1]
    macd, macd_signal = calculate_macd(series)
    momentum = calculate_momentum(series, 5).iloc[-1]
    news_sentiment = analyze_news_sentiment(news)

    state = {
        "symbol": symbol,
        "price": state_price,
        "ema": float(ema),
        "rsi": float(rsi),
        "macd": float(macd.iloc[-1]),
        "macd_signal": float(macd_signal.iloc[-1]),
        "momentum": float(momentum),
        "news_sentiment": float(news_sentiment),
        "social_sentiment": float(social.get("score", 0)),
    }

    state["composite_signal"] = aggregate_signal(
        state["ema"], state["rsi"], state["macd"], state["news_sentiment"], state["social_sentiment"]
    )

    order = TraderAgent().decide(state)
    logging.info("Agent decision: %s", order)

    order["qty"] = RiskManager().size_order(capital, state["price"])
    if order["action"] == "hold":
        order["qty"] = 0

    # risk controls
    order["price"] = state["price"]
    order["stop_loss"] = round(state["price"] * 0.98, 4)
    order["trailing_stop_pct"] = 0.015 if order["action"] == "buy" else None

    approved = RiskManager().check_order(order, capital=capital, equity_history=[capital, capital * 0.98])
    logging.info("Risk check: %s", approved)

    if not approved["allow"]:
        logging.info("Order rejected: %s", approved.get("reason"))
        return

    if order["action"] == "hold":
        logging.info("No order executed (hold)")
        return

    if not (ALPACA_API_KEY and ALPACA_SECRET_KEY):
        logging.warning("Missing Alpaca keys: skipping live order execution")
        return

    try:
        result = AlpacaExecutor().execute_order(order)
        logging.info("Order submitted: %s", result)

        if order["action"] == "buy":
            position_manager.set_position(symbol, order["qty"], state["price"], order["stop_loss"], order["trailing_stop_pct"])
        else:
            position_manager.clear_position()

    except Exception as e:
        logging.error("Execution failed: %s", e)


if __name__ == "__main__":
    run_cycle()

