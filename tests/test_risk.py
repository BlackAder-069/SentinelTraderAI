from risk.risk_manager import RiskManager


def test_risk_allow_hold():
    result = RiskManager().check_order({"action": "hold"}, 100000)
    assert result["allow"] is True


def test_risk_reject_invalid_action():
    result = RiskManager().check_order({"action": "jump"}, 100000)
    assert result["allow"] is False


def test_risk_reject_large_order():
    result = RiskManager().check_order({"action": "buy", "symbol": "SPY", "qty": 1000, "price": 500}, 100000)
    assert result["allow"] is False


def test_risk_reject_missing_price():
    result = RiskManager().check_order({"action": "buy", "symbol": "SPY", "qty": 1}, 100000)
    assert result["allow"] is False


def test_risk_drawdown_exceeded():
    history = [100000, 95000, 92000, 99000, 90000]
    result = RiskManager().check_order({"action": "buy", "symbol": "SPY", "qty": 1, "price": 100}, 100000, equity_history=history)
    assert result["allow"] is False


def test_size_order():
    qty = RiskManager().size_order(100000, 500)
    assert qty > 0


