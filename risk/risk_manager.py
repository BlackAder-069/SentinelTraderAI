from typing import Dict, List
from config import RISK_MAX_DRAWDOWN, RISK_BASE_ORDER_SIZE


class RiskManager:
    def check_order(self, order: Dict, capital: float, equity_history: List[float] = None) -> Dict:
        if order.get("action") not in ["buy", "sell", "hold"]:
            return {"allow": False, "reason": "invalid_action"}

        if order["action"] == "hold":
            return {"allow": True, "reason": "no_action"}

        qty = order.get("qty", 0)
        if not isinstance(qty, (int, float)) or qty <= 0:
            return {"allow": False, "reason": "quantity_must_be_positive"}

        price = order.get("price")
        if price is None or price <= 0:
            return {"allow": False, "reason": "price_required_for_trade"}

        notional = price * qty
        max_notional = capital * RISK_BASE_ORDER_SIZE
        if max_notional > 0 and notional > max_notional:
            return {"allow": False, "reason": "order_too_large"}

        if equity_history:
            dd = self.check_drawdown(equity_history)
            if dd > RISK_MAX_DRAWDOWN:
                return {"allow": False, "reason": "drawdown_exceeded", "drawdown": dd}

        return {"allow": True, "reason": "approved", "notional": notional}

    def check_drawdown(self, equity_history: List[float]) -> float:
        if not equity_history:
            return 0.0

        peak = equity_history[0]
        max_drop = 0.0
        for v in equity_history:
            peak = max(peak, v)
            drawdown = (peak - v) / peak if peak > 0 else 0
            max_drop = max(max_drop, drawdown)
        return round(max_drop, 6)

    def size_order(self, capital: float, price: float, target_pct: float = None) -> int:
        if price <= 0:
            return 0
        if target_pct is None:
            target_pct = RISK_BASE_ORDER_SIZE
        qty = int((capital * target_pct) / price)
        return max(qty, 0)

