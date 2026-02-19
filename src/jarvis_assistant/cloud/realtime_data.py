from __future__ import annotations


class RealtimeDataProvider:
    def weather(self, city: str) -> dict:
        return {"city": city, "summary": "clear", "temperature_c": 23}

    def news(self, topic: str) -> list[dict]:
        return [{"title": f"Sample headline about {topic}", "source": "demo"}]

    def stocks(self, symbol: str) -> dict:
        return {"symbol": symbol, "price": 100.0, "change": 0.5}
