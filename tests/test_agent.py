from agent.langchain_agent import TraderAgent


def test_agent_fallback_buy():
    state = {
        "symbol": "SPY",
        "price": 500,
        "rsi": 20,
        "macd": 1.0,
        "momentum": 0.05,
        "news_sentiment": 0.1,
        "social_sentiment": 0.2,
    }
    agent = TraderAgent()
    decision = agent.decide(state)
    assert decision["action"] in ["buy", "hold"]


def test_agent_fallback_hold():
    state = {"symbol": "SPY", "price": 500, "rsi": 50, "macd": 0.0, "momentum": 0.0}
    agent = TraderAgent()
    decision = agent.decide(state)
    assert decision["action"] == "hold"


def test_agent_memory_persistence():
    from agent.rag_memory import RAGMemory

    memory = RAGMemory(memory_path="test_agent_memory.json")
    memory.add_interaction("query1", "response1")
    related = memory.get_relevant("query1", top_k=1)

    assert related and related[0]["response"] == "response1"

    import os
    if os.path.exists("test_agent_memory.json"):
        os.remove("test_agent_memory.json")


