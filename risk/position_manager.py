import json
import os
from typing import Dict, Optional


class PositionManager:
    def __init__(self, file_path: str = "position_state.json"):
        self.file_path = file_path
        self.position: Optional[Dict] = None
        self._load()

    def _load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.position = json.load(f)
            except Exception:
                self.position = None

    def _save(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.position, f, indent=2)
        except Exception:
            pass

    def get_position(self) -> Optional[Dict]:
        return self.position

    def set_position(self, symbol: str, qty: int, entry_price: float, stop_loss: float, trailing_pct: float):
        self.position = {
            "symbol": symbol,
            "qty": qty,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "trailing_pct": trailing_pct,
            "trailing_stop": round(entry_price * (1 - trailing_pct), 4),
        }
        self._save()

    def clear_position(self):
        self.position = None
        self._save()
