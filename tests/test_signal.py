import pandas as pd
from signal_processing.technical import calculate_ema, calculate_rsi, calculate_macd, calculate_momentum, aggregate_signal


def test_calculate_ema():
    series = pd.Series([1, 2, 3, 4, 5, 6])
    ema = calculate_ema(series, 3)
    assert len(ema) == 6
    assert ema.iloc[-1] > 0


def test_calculate_rsi():
    series = pd.Series([1, 2, 3, 4, 5, 4, 3, 2, 1])
    rsi = calculate_rsi(series, 3)
    assert len(rsi) == 9
    assert rsi.iloc[-1] <= 100


def test_calculate_macd():
    series = pd.Series([1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1])
    macd, signal = calculate_macd(series)
    assert len(macd) == len(series)
    assert len(signal) == len(series)


def test_calculate_momentum():
    series = pd.Series([1, 2, 4, 8, 16])
    momentum = calculate_momentum(series, 1)
    assert momentum.iloc[-1] == 1.0


def test_aggregate_signal():
    score = aggregate_signal(ema=100, rsi=20, macd=1.5, news_sentiment=0.2, social_sentiment=-0.1)
    assert -1.0 <= score <= 1.0


def test_analyze_news_sentiment_empty():
    from signal_processing.finbert_sentiment import analyze_news_sentiment

    score = analyze_news_sentiment([])
    assert score == 0.0


def test_analyze_news_sentiment_fallback():
    from signal_processing.finbert_sentiment import analyze_news_sentiment

    score = analyze_news_sentiment([{"title": "Company reports positive earnings"}])
    assert -1.0 <= score <= 1.0


