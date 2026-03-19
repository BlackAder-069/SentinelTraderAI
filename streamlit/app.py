import os
import sys

import streamlit as st
import pandas as pd

# Ensure project root is on Python path when running `streamlit run streamlit/app.py`.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from ingestion.yahoo_ingestor import YahooIngestor
from ingestion.news_ingestor import NewsIngestor
from ingestion.social_sentiment_ingestor import SocialSentimentIngestor
from signal_processing.technical import calculate_ema, calculate_rsi, calculate_macd, calculate_momentum, aggregate_signal
from signal_processing.finbert_sentiment import analyze_news_sentiment
from agent.langchain_agent import TraderAgent
from risk.risk_manager import RiskManager
from execution.alpaca_executor import AlpacaExecutor

st.title("Agentic AI Trader Bot")

symbol = st.sidebar.text_input("Symbol", "SPY")
period = st.sidebar.selectbox("Period", ["7d", "30d", "60d"], index=1)
interval = st.sidebar.selectbox("Interval", ["1d", "1h", "15m"], index=0)
run = st.sidebar.button("Run Cycle")

if run:
    df = YahooIngestor().fetch_ohlcv(symbol, period=period, interval=interval)
    if df.empty:
        st.warning("No data for symbol")
    else:
        st.subheader("Price data")
        st.dataframe(df.tail(10))

        series = df["Close"].dropna()
        ema12 = calculate_ema(series, 12)
        rsi14 = calculate_rsi(series, 14)
        macd, macd_signal = calculate_macd(series)
        momentum = calculate_momentum(series, 5)

        st.line_chart(pd.DataFrame({"Close": series, "EMA12": ema12}))
        st.line_chart(pd.DataFrame({"RSI14": rsi14}))

        news = NewsIngestor().fetch_news(symbol)
        social = SocialSentimentIngestor().fetch_social_sentiment(symbol)
        news_score = analyze_news_sentiment(news)

        state = {
            "symbol": symbol,
            "price": float(series.iloc[-1]),
            "ema": float(ema12.iloc[-1]),
            "rsi": float(rsi14.iloc[-1]),
            "macd": float(macd.iloc[-1]),
            "momentum": float(momentum.iloc[-1]),
            "news_sentiment": news_score,
            "social_sentiment": social.get("score", 0),
        }

        state["composite_signal"] = aggregate_signal(
            state["ema"], state["rsi"], state["macd"], state["news_sentiment"], state["social_sentiment"]
        )

        order = TraderAgent().decide(state)
        order["qty"] = RiskManager().size_order(100000, state["price"]) if order["action"] != "hold" else 0

        st.write("State:", state)
        st.write("Proposed order:", order)

        approval = RiskManager().check_order(order, capital=100000)
        st.write("Risk approval:", approval)

        if approval["allow"] and order["action"] != "hold":
            st.write("Sending order to Alpaca paper mode...")
            try:
                result = AlpacaExecutor().execute_order(order)
                st.write("Order submitted:", result)
            except Exception as e:
                st.error(f"Execution error: {e}")
