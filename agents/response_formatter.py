from typing import Dict, Any


# #[ИЗ RAW]: class ResponseGenerator:
# #[ИЗМЕНЕНО]: Переименовано в ResponseFormatter для соответствия архитектуре.
class ResponseFormatter:
    """
    Генератор аналитических отчетов на основе результатов NLP-маршрутизатора и поиска.
    Отвечает в строгом, но читаемом Markdown-формате.
    """

    def __init__(self):
        pass

    # #[ИЗ RAW]: def generate_response(self, query_analysis: Dict[str, Any], search_results: Dict[str, Any]) -> str:
    def format_response(self, routed_data: Dict[str, Any], search_results: Dict[str, Any]) -> str:
        """
        Генерирует ответ на основе анализа запроса (intent) и результатов поиска.
        """
        intent = routed_data.get("intent", "unknown")
        params = routed_data.get("parameters", {})
        original_query = routed_data.get("original_query", "")

        # #[ИЗ RAW]: if intent == "find_build":
        # #[ИЗМЕНЕНО]: Адаптация под финансовые интенты из intent_router.py
        if intent == "analyze_portfolio":
            tier = params.get("risk_tier")
            tags = params.get("market_tags", [])
            p_type = params.get("portfolio_type", "Сбалансированный")

            # #[ИЗ RAW]: gems_objects = search_results.get("recommended_gems", [])
            # #[ИЗМЕНЕНО]: Гемы -> Core Assets, Пассивки -> Derivatives, Предметы -> Bonds
            assets_objects = search_results.get("core_assets", [])
            deriv_objects = search_results.get("derivatives", [])
            bonds_objects = search_results.get("bonds", [])

            assets = [a.get('name', 'Unknown Asset') for a in assets_objects]
            derivatives = [d.get('name', 'Unknown Derivative') for d in deriv_objects]
            bonds = [b.get('type', 'Unknown Bond') for b in bonds_objects]

            if tier:
                tag_str = ", ".join(tags) if tags else "стандартные условия"
                response = f"### 🧠 **ПОРТФЕЛЬ ДЛЯ УРОВНЯ РИСКА T{tier} ({tag_str})**\n\n"
                response += f"**Тип стратегии:** {p_type}\n"
                if assets:
                    response += f"**Базовые активы:** {', '.join(assets)}\n"
                    # #[ИЗ RAW]: if "Physical" in gems: response += "> 💡 **Пояснение:** Используются гемы физического урона..."
                    if "Crypto" in assets or "BTC" in assets:
                        response += "> 💡 **Пояснение:** Используются высоковолатильные активы для максимизации Alpha.\n"
                if derivatives:
                    response += f"**Инструменты хеджирования:** {', '.join(derivatives)}\n"
                if bonds:
                    response += f"**Защитные активы:** {', '.join(bonds)}\n"
                response += "\n> 💡 **Совет:** Используйте алгоритмический ребалансинг и жесткие стоп-лоссы для этой стратегии."
                return response
            else:
                return "❌ Не удалось определить уровень риска (Tier). Пожалуйста, уточните (например, 'Какой портфель на Т1 с волатильностью?')."

        # #[ИЗ RAW]: elif intent == "find_gems":
        elif intent == "find_assets":
            asset_class = params.get("asset_class")
            assets_objects = search_results.get("assets", [])
            asset_names = [a.get('name', 'Unknown Asset') for a in assets_objects]

            if asset_names:
                response = f"### 🔥 **ИНСТРУМЕНТЫ НА РЫНКЕ: {asset_class.upper()}**\n\n"
                response += f"- {', '.join(asset_names)}\n\n"
                response += "> 💡 **Совет:** Обязательно используйте `Smart Routing` для минимизации проскальзывания (slippage).\n"
                if len(asset_names) > 1:
                    response += f"> 🔍 **Пояснение:** Эти инструменты показывают наивысшую ликвидность в секторе {asset_class.lower()}."
                return response
            else:
                return f"❌ Не найдено ликвидных инструментов для рынка {asset_class}."

        # #[ИЗ RAW]: elif intent == "check_survivability":
        elif intent == "check_risk":
            # #[ИЗ RAW]: drawdown = params.get("drawdown", 0)
            # #[ИЗМЕНЕНО]: Защита от TypeError. Если ключ равен None, or 0 превратит его в 0.
            drawdown = params.get("drawdown") or 0
            hedge_ratio = params.get("hedge_ratio") or 0.0
            context = params.get("context") or "general"

            recovery_rate = drawdown * hedge_ratio * 0.2

            if recovery_rate > 10:
                status = "✅ **ПОРТФЕЛЬ УСТОЙЧИВ**"
                reason = f"Коэффициент восстановления {recovery_rate:.1f} — капитал защищен от маржин-колла."
            else:
                status = "❌ **ВЫСОКИЙ РИСК ЛИКВИДАЦИИ**"
                reason = f"Коэффициент восстановления {recovery_rate:.1f} — возможна полная потеря средств."

            response = f"### ⚔️ **СТРЕСС-ТЕСТ: {context.upper()}**\n\n"
            response += f"- **Допустимая просадка:** {drawdown}%\n"
            response += f"- **Коэффициент хеджирования:** {hedge_ratio * 100:.1f}%\n"
            response += f"- **Метрика восстановления:** {recovery_rate:.1f}\n\n"
            response += f"> {status} — {reason}\n"

            if status == "❌ **ВЫСОКИЙ РИСК ЛИКВИДАЦИИ**":
                response += f"> 💡 **Совет:** Увеличьте долю защитных активов (Bonds) до 40% или используйте опционы Put.\n"
            return response

        else:
            # #[ИЗ RAW]: return f"❌ Неизвестный запрос: `{original_question}`..."
            return f"❌ Неизвестный запрос: `{original_query}`. Пока не могу точно понять. Попробуйте переформулировать (например, 'портфель на Т1', 'активы на крипто', 'выживет ли в кризис')."


# #[ДОБАВЛЕНО]: Блок для локального тестирования
if __name__ == "__main__":
    formatter = ResponseFormatter()

    # Имитация данных от роутера и поисковика
    mock_routed_data = {
        "intent": "analyze_portfolio",
        "parameters": {"risk_tier": 1, "market_tags": ["Volatile"], "portfolio_type": "Aggressive"}
    }
    mock_search_results = {
        "core_assets": [{"name": "BTC/USDT"}, {"name": "ETH/USDT"}],
        "derivatives": [{"name": "BTC-PERP-Options"}],
        "bonds": [{"type": "US Treasuries"}]
    }

    print(formatter.format_response(mock_routed_data, mock_search_results))