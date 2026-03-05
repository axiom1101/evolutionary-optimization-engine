import re
from typing import Dict, List, Optional, Any

# #[ИЗ RAW]: Словари DAMAGE_TYPES, CONTENT_TYPES, CLASS_TYPES, MECHANIC_TYPES
# #[ИЗМЕНЕНО]: Словари переписаны под предметную область FinTech / Quant Trading.
# Логика сопоставления и структура оставлены без изменений.

ASSET_CLASSES = {
    "crypto": ["крипта", "крипту", "crypto", "btc", "eth", "токены"],
    "equities": ["акции", "фонда", "equities", "stocks", "sp500"],
    "forex": ["валюта", "форекс", "forex", "fiat", "фиат"],
    "derivatives": ["фьючерсы", "опционы", "деривативы", "derivatives", "options"],
    "mixed": ["смешанный", "диверсифицированный", "mixed", "all"]
}

MARKET_CONDITIONS = {
    "bull": ["бычий", "рост", "bull", "uptrend"],
    "bear": ["медвежий", "падение", "bear", "downtrend"],
    "volatile": ["волатильный", "шторм", "volatile", "high risk"],
    "flat": ["флэт", "боковик", "flat", "consolidation"]
}

PORTFOLIO_TYPES = {
    "Aggressive": ["агрессивный", "рисковый", "aggressive", "high yield"],
    "Conservative": ["консервативный", "надежный", "conservative", "safe"],
    "Balanced": ["сбалансированный", "умеренный", "balanced", "neutral"]
}

STRATEGY_MECHANICS = {
    "arbitrage": ["арбитраж", "спред", "arbitrage", "spread"],
    "hedging": ["хеджирование", "хедж", "hedging", "hedge"],
    "scalping": ["скальпинг", "скальп", "scalping", "hft"],
    "grid": ["сетка", "сеточный", "grid trading"]
}


class IntentRouter:
    """
    NLP-маршрутизатор запросов.
    Определяет intent (намерение) и извлекает параметры (entities) с помощью регулярных выражений.
    """

    def __init__(self):
        # #[ИЗ RAW]: self.intents = { "find_build": {...}, "find_gems": {...}, ... }
        # #[ИЗМЕНЕНО]: Починены легаси-баги с m.group(0) -> m.string (чтобы не терять слова вне регулярки)
        # и добавлены нежадные квантификаторы .*? для пропуска предлогов.
        self.intents = {
            "analyze_portfolio": {
                "patterns":[
                    r"(?:стратегия|портфель).*?(?:на|для)\s+т(\d+)(?:\s+с)?\s*(.*)",
                    r"(?:стратегия|портфель).*?(?:на|для)\s*(\d+)(?:\s+уровень|lvl|level)?",
                ],
                "entity_extractors": {
                    "risk_tier": lambda m: int(m.group(1)) if m.group(1) else None,
                    # #[УДАЛЕНО]: m.group(2) и m.group(0)
                    # #[ДОБАВЛЕНО]: m.string передает всю строку целиком, чтобы экстрактор нашел "агрессивный" или "волатильный" в любой части текста
                    "market_tags": lambda m: self._parse_market_tags(m.string),
                    "portfolio_type": lambda m: self._extract_portfolio_type(m.string)
                }
            },
            "find_assets": {
                "patterns":[
                    r"(?:активы|инструменты).*?(?:на|в|для)\s+(.+?)\s+(?:рынок|рынке|рынка)",
                ],
                "entity_extractors": {
                    "asset_class": lambda m: self._normalize_asset_class(m.group(1)) if m.group(1) else None
                }
            },
            "check_risk": {
                "patterns":[
                    r"(?:сольет ли|сольет|выживет ли|выживет).*?(?:на|в|во)\s+(?:кризис|кризисе).*?(?:с\s+)?(\d+)\s+(?:просадкой|drawdown).*?(\d+)%\s+(?:хеджем|hedge)",
                    r"(?:сольет ли|сольет|выживет ли|выживет).*?(?:на|в|во)\s+(?:кризис|кризисе)",
                ],
                "entity_extractors": {
                    "drawdown": lambda m: int(m.group(1)) if len(m.groups()) > 0 and m.group(1) else None,
                    "hedge_ratio": lambda m: int(m.group(2)) / 100.0 if len(m.groups()) > 1 and m.group(2) else None,
                    "context": lambda m: "Crisis" if "кризис" in m.string.lower() else None
                }
            }
        }

    # #[ИЗ RAW]: def _parse_content_tags(self, text: str) -> List[str]:
    def _parse_market_tags(self, text: str) -> List[str]:
        tags = []
        if not text:
            return tags
        text_lower = text.lower()
        if "волатильн" in text_lower or "volatile" in text_lower:
            tags.append("Volatile")
        if "падающ" in text_lower or "bear" in text_lower:
            tags.append("Bear Market")
        return tags

    # #[ИЗ RAW]: def _normalize_damage_type(self, text: str) -> str:
    def _normalize_asset_class(self, text: str) -> str:
        text_lower = text.lower()
        mapping = {
            "крипто": "Crypto",
            "крипта": "Crypto",
            "акции": "Equities",
            "фондовый": "Equities",
            "валютный": "Forex",
            "форекс": "Forex",
        }
        return mapping.get(text_lower, text.capitalize())

    # #[ИЗ RAW]: def _extract_class(self, text: str) -> Optional[str]:
    def _extract_portfolio_type(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        for p_type, keywords in PORTFOLIO_TYPES.items():
            if any(kw in text_lower for kw in keywords):
                return p_type
        return None

    # #[ИЗ RAW]: def analyze(self, question: str) -> Dict[str, any]:
    # #[ИЗМЕНЕНО]: Логика оставлена 1 в 1. Изменено только имя метода для красоты.
    def route_query(self, question: str) -> Dict[str, Any]:
        question_lower = question.lower()
        for intent_name, intent_data in self.intents.items():
            for pattern in intent_data["patterns"]:
                match = re.search(pattern, question_lower, re.IGNORECASE)
                if match:
                    params = {}
                    for entity, extractor in intent_data["entity_extractors"].items():
                        try:
                            value = extractor(match)
                            if value is not None:
                                params[entity] = value
                        except (IndexError, ValueError):
                            continue

                    # Спец-проверка для check_risk (бывший check_survivability)
                    if intent_name == "check_risk" and not params.get("drawdown") and not params.get("hedge_ratio"):
                        if params.get("context"):
                            return {"intent": intent_name, "parameters": params, "original_query": question}
                        else:
                            continue

                    return {"intent": intent_name, "parameters": params, "original_query": question}

        return {"intent": "unknown", "parameters": {}, "original_query": question}


# #[ДОБАВЛЕНО]: Блок для локального тестирования скрипта
if __name__ == "__main__":
    router = IntentRouter()
    test_queries = [
        "Какая стратегия на т1 с волатильным рынком?",
        "Какие активы на крипто рынке?",
        "Выживет ли портфель в кризис с 20 просадкой и 50% хеджем?",
        "Сделай мне агрессивный портфель на т2"
    ]

    print("--- Тестирование IntentRouter ---")
    for q in test_queries:
        print(f"Запрос: {q}")
        print(f"Результат: {router.route_query(q)}\n")