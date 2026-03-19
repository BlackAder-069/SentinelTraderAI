from alpaca_trade_api.rest import REST
from config import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL

class AlpacaExecutor:
    def __init__(self):
        self.client = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL, api_version='v2')

    def execute_order(self, order: dict):
        action = order.get("action")
        symbol = order.get("symbol")
        qty = order.get("qty", 0)
        stop_loss = order.get("stop_loss")
        trailing_stop_pct = order.get("trailing_stop_pct")

        if action not in ["buy", "sell"] or qty <= 0 or not symbol:
            raise ValueError("Invalid order payload")

        if trailing_stop_pct is not None:
            return self.client.submit_order(
                symbol=symbol,
                qty=qty,
                side=action,
                type="market",
                time_in_force="day",
                order_class="trailing_stop",
                trail_percent=trailing_stop_pct * 100,
            )

        if stop_loss is not None:
            return self.client.submit_order(
                symbol=symbol,
                qty=qty,
                side=action,
                type="market",
                time_in_force="day",
                order_class="bracket",
                stop_loss={"stop_price": stop_loss},
            )

        return self.client.submit_order(symbol=symbol, qty=qty, side=action, type="market", time_in_force="day")

    def close_position(self, symbol: str):
        return self.client.close_position(symbol)
