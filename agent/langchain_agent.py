import json
from typing import Dict

from config import GEMINI_API_KEY

HumanMessage = None
SystemMessage = None
LanguageModel = None

try:
    from langchain.schema import HumanMessage, SystemMessage
except ImportError:
    HumanMessage = None
    SystemMessage = None

try:
    from langchain.chat_models import ChatOpenAI
    LanguageModel = ChatOpenAI
except Exception:
    try:
        from langchain import OpenAI
        LanguageModel = OpenAI
    except Exception:
        LanguageModel = None


class TraderAgent:
    def __init__(self):
        self.model = None
        if LanguageModel is not None and GEMINI_API_KEY:
            try:
                self.model = LanguageModel(
                    model_name="gemini-1.5-pro",
                    openai_api_key=GEMINI_API_KEY,
                    temperature=0.0,
                    max_tokens=300,
                )
            except Exception:
                self.model = None

        self.system_prompt = (
            "You are a trading decision engine. Given a numeric market state (price, RSI, MACD, momentum, news sentiment, social sentiment), "
            "choose one action: buy/sell/hold and quantity as integer. Return JSON with keys: action, symbol, qty, reason."
        )

    def decide(self, state: Dict) -> Dict:
        message = (
            "Analyze the following market state and produce a trading action:\n"
            f"{json.dumps(state, indent=2)}\n"
            "Guidelines:\n"
            "- RSI < 30, momentum > 0, sentiment > 0 => buy.\n"
            "- RSI > 70, momentum < 0, sentiment < 0 => sell.\n"
            "- Otherwise hold.\n"
            "Return valid JSON only."
        )

        if self.model:
            try:
                if HumanMessage and SystemMessage:
                    response = self.model([
                        SystemMessage(content=self.system_prompt),
                        HumanMessage(content=message),
                    ])
                else:
                    prompt = self.system_prompt + "\n" + message
                    response = self.model(prompt) if callable(self.model) else None

                if response is not None:
                    text = self._extract_text(response)
                    decision = self._parse_decision(text)
                    if self._is_valid_decision(decision):
                        return decision
            except Exception:
                pass

        return self._fallback_decision(state)

    @staticmethod
    def _extract_text(response) -> str:
        if isinstance(response, str):
            return response.strip()
        if hasattr(response, "content"):
            return response.content.strip()
        if hasattr(response, "generations"):
            try:
                return str(response.generations[0][0].text).strip()
            except Exception:
                pass
        return str(response).strip()

    @staticmethod
    def _parse_decision(text: str) -> Dict:
        try:
            if text.startswith('```'):
                text = text.strip('`')
            return json.loads(text)
        except Exception:
            return {}

    @staticmethod
    def _is_valid_decision(decision: Dict) -> bool:
        if not isinstance(decision, dict):
            return False
        if decision.get('action') not in ['buy', 'sell', 'hold']:
            return False
        if not isinstance(decision.get('qty'), int):
            return False
        if decision['action'] == 'hold' and decision.get('qty', 0) != 0:
            return False
        return True

    @staticmethod
    def _fallback_decision(state: Dict) -> Dict:
        rsi = float(state.get('rsi', 50))
        momentum = float(state.get('momentum', 0))
        news = float(state.get('news_sentiment', 0))
        social = float(state.get('social_sentiment', 0))
        macd = float(state.get('macd', 0))
        symbol = state.get('symbol', 'UNKNOWN')

        if rsi < 30 and momentum > 0 and macd > 0 and (news + social) > 0:
            return {'action': 'buy', 'symbol': symbol, 'qty': 1, 'reason': 'fallback_strong_buy'}
        if rsi > 70 and momentum < 0 and macd < 0 and (news + social) < 0:
            return {'action': 'sell', 'symbol': symbol, 'qty': 1, 'reason': 'fallback_strong_sell'}

        if rsi < 40 and momentum > 0:
            return {'action': 'buy', 'symbol': symbol, 'qty': 1, 'reason': 'fallback_buy_momentum'}
        if rsi > 60 and momentum < 0:
            return {'action': 'sell', 'symbol': symbol, 'qty': 1, 'reason': 'fallback_sell_momentum'}

        return {'action': 'hold', 'symbol': symbol, 'qty': 0, 'reason': 'fallback_hold'}

