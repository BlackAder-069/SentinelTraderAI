import pandas as pd


def calculate_ema(series: pd.Series, period: int=14) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def calculate_rsi(series: pd.Series, period: int=14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / (avg_loss.replace(0, 1e-9))
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(series: pd.Series, fast: int=12, slow: int=26, signal_period: int=9):
    ema_fast = calculate_ema(series, fast)
    ema_slow = calculate_ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    return macd_line, signal_line


def calculate_momentum(series: pd.Series, period: int=5) -> pd.Series:
    return series.pct_change(periods=period).fillna(0)


def aggregate_signal(ema: float, rsi: float, macd: float, news_sentiment: float, social_sentiment: float) -> float:
    score = 0.0
    score += 0.4 * (1 if ema is not None else 0) * (1 if macd > 0 else -1)
    score += 0.3 * ((50 - rsi) / 50) if rsi is not None else 0
    score += 0.15 * news_sentiment
    score += 0.15 * social_sentiment
    # normalize to range [-1,1]
    if score > 1:
        score = 1.0
    if score < -1:
        score = -1.0
    return round(score, 4)

