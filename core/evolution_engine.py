import json
import random
import math
import copy
import os
import configparser
from typing import List, Dict, Any, Tuple

# #[ДОБАВЛЕНО]: Подключаем наш единый клиент LLM и конфиги
from agents.llm_client import ask_ollama, DEMO_MODE

# -------------------------
# Настройки Генетического Алгоритма
# -------------------------
# #[ИЗ RAW]: OLLAMA_MODEL = "qwen3:8b"
# #[УДАЛЕНО]: Хардкод модели. Теперь модель берется из llm_client.

POPULATION_SIZE = 30
GENERATIONS = 25
MUTATION_RATE = 0.25
TOP_K = 6  # сколько кандидатов оставляем для кроссовера/мутации (Элитизм)

# #[ИЗ RAW]: WEIGHTS = { "clear_speed": 1.3, "boss_dps": 1.2, "mobility": 1.0, "sustain": 1.1, "automation": 1.0 }
# #[ИЗМЕНЕНО]: Веса фитнес-функции переведены на язык количественных финансов.
WEIGHTS = {
    "yield_potential": 1.3,  # Бывший clear_speed (Потенциальная доходность)
    "alpha_generation": 1.2,  # Бывший boss_dps (Генерация альфы / Пиковая доходность)
    "liquidity": 1.0,  # Бывший mobility (Ликвидность активов)
    "risk_mitigation": 1.1,  # Бывший sustain (Защита от просадок / Хеджирование)
    "algorithmic_execution": 1.0  # Бывший automation (Степень автоматизации стратегии)
}


# -------------------------

# #[ИЗ RAW]: def ask_ollama(user_prompt: str, model: str = OLLAMA_MODEL) -> str:
# #[УДАЛЕНО]: Дублирующаяся функция вызова Ollama. Мы используем единую из agents.llm_client.

# -------------------------
# ЗАГРУЗКА И ПРЕДОБРАБОТКА ДАННЫХ (Data Preparation)
# -------------------------
def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# #[ИЗ RAW]: def clean_tree(tree: Dict[str, Any]) -> List[Dict[str, Any]]:
# #[ИЗМЕНЕНО]: Рескин. Дерево пассивок -> Граф корреляций рынка.
def clean_correlation_graph(graph_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Возвращаем список узлов графа с полем stats. Исключаем неликвидные или закрытые рынки.
    """
    nodes = graph_data.get("nodes", []) if isinstance(graph_data, dict) else graph_data
    cleaned = []
    for n in nodes:
        name = n.get("name", "")
        # #[ИЗ RAW]: if any(tag in name.upper() for tag in ["[CLUSTER]", "[ANOINMENT]", "[BLIGHTED]"]):
        # #[ИЗМЕНЕНО]: Игровые теги заменены на финансовые (внебиржевые, делистинг, приостановленные)
        if any(tag in name.upper() for tag in ["[OTC]", "[DELISTED]", "[SUSPENDED]"]):
            continue
        stats = n.get("stats", [])
        if not stats:
            continue
        cleaned.append({
            "id": n.get("id"),
            "name": name,
            "stats": stats,
            # #[ИЗ RAW]: "is_ascendency": n.get("is_ascendency", False)
            "is_core_market": n.get("is_core_market", False)  # Базовый рынок (бывшее Ascendancy)
        })
    return cleaned


# #[ИЗ RAW]: def parse_skill_value_range(val: str) -> float:
def parse_asset_value_range(val: str) -> float:
    """
    Для строк вроде "(8-23) Yield" или "+(100-138)%" — берём верхнюю границу.
    Предполагаем, что где есть числа через '-' — берём max.
    """
    import re
    m = re.search(r"(\d+)\s*[\u2013\u2014-]\s*(\d+)", val)
    if m:
        return float(max(int(m.group(1)), int(m.group(2))))
    m2 = re.search(r"(\d+(\.\d+)?)", val)
    if m2:
        return float(m2.group(1))
    return 0.0


# #[ИЗ RAW]: def clean_skills(skills: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
# #[ИЗМЕНЕНО]: Рескин. Скиллы -> Активы. Активные скиллы -> Базовые активы. Саппорты -> Деривативы.
def clean_assets(assets_data: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
    """
    Возвращает (primary_assets, derivatives).
    Для каждого поля с диапазоном используем верхнюю границу.
    """
    primary = []
    derivatives = []
    for s in assets_data.get("skills",
                             []):  # В реальных данных ключ может называться иначе, оставляем для совместимости с RAW
        rec = {
            "id": s.get("id"),
            "name": s.get("name"),
            "tags": s.get("tags", []),
            "raw": s
        }
        numbers = []
        for e in s.get("effects", []) if s.get("effects") else s.get("stat_descriptions", []) if s.get(
                "stat_descriptions") else []:
            if isinstance(e, str):
                numbers.append(parse_asset_value_range(e))
            elif isinstance(e, dict) and e.get("value"):
                numbers.append(parse_asset_value_range(str(e["value"])))
        rec["numbers"] = numbers

        # #[ИЗ RAW]: if "Support" in s.get("tags",[]) or s.get("type") == "Support":
        if "Derivative" in s.get("tags", []) or s.get("type") == "Derivative" or "Support" in s.get("tags", []):
            derivatives.append(rec)
        else:
            primary.append(rec)
    return primary, derivatives


# #[ИЗ RAW]: def load_and_prepare(tree_path: str, skills_path: str, rules_path: str):
def load_market_data(graph_path: str, assets_path: str, rules_path: str):
    graph_raw = load_json(graph_path)
    assets_raw = load_json(assets_path)
    rules_raw = load_json(rules_path)

    graph = clean_correlation_graph(graph_raw)
    primary_assets, derivatives = clean_assets(assets_raw)
    rules = rules_raw

    return graph, primary_assets, derivatives, rules


# -------------------------
# ИНТЕГРАЦИЯ С LLM (ОБЪЯСНЕНИЕ СИНЕРГИЙ)
# -------------------------
# #[ИЗ RAW]: BASE_PROMPT_TEMPLATE = """У тебя есть JSON-пакет с билдом Path of Exile..."""
# #[ИЗМЕНЕНО]: Промпт переписан под финансового аналитика.
BASE_PROMPT_TEMPLATE = """
У тебя есть JSON-пакет с конфигурацией инвестиционного портфеля. Задача: объяснить, почему предложенная стратегия неочевидна и оценить ее по метрикам.
Формат входа: {{ "portfolio": <portfolio_json>, "meta": <meta_json> }}.
Требуется кратко:
1) Ключевая механика арбитража (1-2 предложения).
2) Почему эта связка активов неочевидна (1-3 буллета).
3) Оценки: yield_potential, alpha_generation, liquidity, risk_mitigation, algorithmic_execution — числа 0..10 и короткая причина.
4) Проверка на соответствие риск-правилам (rules.json): да/нет + перечислить нарушения.
Отвечай по-русски в компактном JSON.
"""


# #[ИЗ RAW]: def ask_model_explain(build: Dict, meta: Dict) -> Dict:
def explain_portfolio_strategy(portfolio: Dict, meta: Dict) -> Dict:
    payload = {"portfolio": portfolio, "meta": meta}
    prompt = BASE_PROMPT_TEMPLATE + "\n\nInput:\n" + json.dumps(payload, ensure_ascii=False)

    # Используем нашу обертку из agents/llm_client.py
    resp = ask_ollama(system_prompt="Ты Senior Quant Analyst.", user_prompt=prompt)

    try:
        parsed = json.loads(resp)
        return parsed
    except Exception:
        return {"raw_text": resp}


# -------------------------
# ГЕНЕРАЦИЯ КАНДИДАТОВ (Random Initialization)
# -------------------------
# #[ИЗ RAW]: def random_build(active_pool: List[Dict], support_pool: List[Dict], tree: List[Dict], rules: Dict) -> Dict:
# #[ИЗМЕНЕНО]: Рескин. Билд -> Портфель. Активные скиллы -> Базовые активы. Саппорты -> Деривативы.
def generate_random_portfolio(primary_pool: List[Dict], derivative_pool: List[Dict], graph: List[Dict],
                              rules: Dict) -> Dict:
    """
    Создаёт случайный допустимый инвестиционный портфель:
     - выбирает базовый рынок (если есть)
     - выбирает до 5 базовых активов
     - для каждого актива подбирает 3-5 деривативов (хедж/плечо)
    """
    portfolio = {"primary_assets": [], "core_market": None, "correlation_nodes": [],
                 "allocations": rules.get("slots", {})}

    # #[ИЗ RAW]: asc_options = [n for n in tree if n.get("is_ascendency")]
    market_options = [n for n in graph if n.get("is_core_market")]
    if market_options:
        chosen = random.choice(market_options)
        portfolio["core_market"] = chosen.get("name")

    max_primary = min(5, rules.get("max_active", 5))
    n_primary = random.randint(1, max_primary)
    chosen_primary = random.sample(primary_pool, min(n_primary, len(primary_pool)))

    for a in chosen_primary:
        n_derivs = random.randint(3, 5)
        derivs = random.sample(derivative_pool, min(n_derivs, len(derivative_pool)))
        portfolio["primary_assets"].append({
            "asset": a["name"],
            "derivatives": [s["name"] for s in derivs]
        })

    # Простая аллокация — рандомные значимые узлы корреляции
    portfolio["correlation_nodes"] = [n["name"] for n in random.sample(graph, min(12, len(graph)))]
    return portfolio


# -------------------------
# СКОРОВАНИЕ (Heuristic Fitness Function)
# -------------------------
# #[ИЗ RAW]: def heuristic_score(build: Dict) -> Dict[str, float]:
def heuristic_score(portfolio: Dict) -> Dict[str, float]:
    """
    Быстрая эвристика (O(1) complexity screener): оцениваем портфель по базовым признакам.
    Возвращаем breakdown и aggregated score.
    """
    yield_pot = 0.0
    alpha_gen = 0.0
    liquidity = 0.0
    risk_mit = 0.0
    algo_exec = 0.0

    for a in portfolio["primary_assets"]:
        # #[ИЗ RAW]: длина имени как proxy для сложности — (только эвристика)
        # #[ИЗМЕНЕНО]: Оставляем эту гениальную заглушку-эвристику из оригинала
        ks = len(a["asset"])
        yield_pot += ks * 0.1
        alpha_gen += ks * 0.08

        # #[ИЗ RAW]: supports count helps clear speed
        derivs_n = len(a["derivatives"])
        yield_pot += derivs_n * 0.6
        alpha_gen += derivs_n * 0.3

        # #[ИЗ RAW]: if "Totem" in a["skill"] or "Minion" in a["skill"]: automation += 2.0
        if "HFT" in a["asset"] or "Algo" in a["asset"]:
            algo_exec += 2.0

    # Базовая нормализация (ограничиваем сверху 10.0)
    metrics = {
        "yield_potential": min(10.0, yield_pot / 2.0),
        "alpha_generation": min(10.0, alpha_gen / 2.0),
        "liquidity": min(10.0, liquidity + random.random() * 2.0),
        "risk_mitigation": min(10.0, risk_mit + random.random() * 2.0),
        "algorithmic_execution": min(10.0, algo_exec + random.random() * 2.0)
    }

    # Aggregated weighted score
    agg = sum(metrics[k] * WEIGHTS.get(k, 1.0) for k in metrics)
    metrics["score"] = agg
    return metrics


# -------------------------
# ЭВОЛЮЦИОННЫЙ ЦИКЛ (Genetic Algorithm Core)
# -------------------------
# #[ИЗ RAW]: def evolve(active_pool, support_pool, tree, rules):
def evolve_portfolios(primary_pool, derivative_pool, graph, rules):
    # Инициализация популяции
    population = [generate_random_portfolio(primary_pool, derivative_pool, graph, rules) for _ in
                  range(POPULATION_SIZE)]
    archive = []

    for gen in range(GENERATIONS):
        scored = []
        for indiv in population:
            heur = heuristic_score(indiv)
            scored.append((heur["score"], indiv, heur))

        # Сортировка по убыванию фитнес-функции
        scored.sort(key=lambda x: x[0], reverse=True)

        # Элитизм (keep top)
        top = scored[:TOP_K]
        archive.extend(top)

        # #[ИЗ RAW]: next_pop = [copy.deepcopy(item[1]) for item in top]
        # #[ДОБАВЛЕНО]: Реализация Пункта 7 из ТЗ "Генетическая эволюция".
        # Добавляем 15% случайных "слабых" портфелей (Wildcards) для сохранения генетического разнообразия.
        wildcards_count = int(POPULATION_SIZE * 0.15)
        remaining_pool = scored[TOP_K:]
        wildcards = [item[1] for item in random.sample(remaining_pool, min(wildcards_count, len(remaining_pool)))]

        next_pop = [copy.deepcopy(item[1]) for item in top] + copy.deepcopy(wildcards)

        # Кроссовер и мутации для заполнения популяции
        while len(next_pop) < POPULATION_SIZE:
            p1 = random.choice(top)[1]
            p2 = random.choice(top)[1]
            child = crossover(p1, p2, primary_pool, derivative_pool, graph)
            if random.random() < MUTATION_RATE:
                child = mutate(child, primary_pool, derivative_pool, graph)
            next_pop.append(child)

        population = next_pop

    # Возвращаем Топ-N уникальных портфелей
    final = sorted(archive, key=lambda x: x[0], reverse=True)
    unique_builds = []
    seen = set()
    for s, b, h in final:
        key = json.dumps(b, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            unique_builds.append((s, b, h))
            seen.add(key)
        if len(unique_builds) >= 10:
            break
    return unique_builds


def crossover(a, b, primary_pool, derivative_pool, graph):
    child = {"primary_assets": [], "core_market": None, "correlation_nodes": []}
    # Mix core market
    child["core_market"] = a.get("core_market") if random.random() < 0.5 else b.get("core_market")

    # Mix primary assets
    a_acts = a.get("primary_assets", [])
    b_acts = b.get("primary_assets", [])
    split = max(1, min(len(a_acts), len(b_acts)) // 2)
    acts = a_acts[:split] + b_acts[split:]
    acts = acts[:5]  # ensure limit

    # Random repair: ensure derivatives exist
    for act in acts:
        if "derivatives" not in act or not act["derivatives"]:
            act["derivatives"] = [random.choice(derivative_pool)["name"] for _ in range(3)]

    child["primary_assets"] = acts

    # #[ИЗ RAW]: child["correlation_nodes"] = (a.get("correlation_nodes", [])[:6] + b.get("correlation_nodes", [])[:6])[:12]
    # #[ИЗМЕНЕНО]: Исправлен баг дублирования узлов. Теперь используем set() для уникальности.
    combined_nodes = list(set(a.get("correlation_nodes", []) + b.get("correlation_nodes", [])))
    child["correlation_nodes"] = random.sample(combined_nodes, min(len(combined_nodes), 6))

    return child


def mutate(portfolio, primary_pool, derivative_pool, graph):
    nb = copy.deepcopy(portfolio)

    # #[ДОБАВЛЕНО]: Мутация графа корреляций (маршрута), которой не было в RAW
    if random.random() < 0.3 and graph:
        new_node = random.choice(graph)["name"]
        if new_node not in nb["correlation_nodes"]:
            if nb["correlation_nodes"]:
                nb["correlation_nodes"].pop(random.randrange(len(nb["correlation_nodes"])))
            nb["correlation_nodes"].append(new_node)

    # Случайно заменить один базовый актив
    if nb["primary_assets"] and random.random() < 0.6:
        idx = random.randrange(len(nb["primary_assets"]))
        nb["primary_assets"][idx] = {
            "asset": random.choice(primary_pool)["name"],
            "derivatives": [random.choice(derivative_pool)["name"] for _ in range(random.randint(3, 5))]
        }
    # Или поменять один дериватив
    else:
        if nb["primary_assets"]:
            act = random.choice(nb["primary_assets"])
            if act["derivatives"]:
                i = random.randrange(len(act["derivatives"]))
                act["derivatives"][i] = random.choice(derivative_pool)["name"]
    return nb


# -------------------------
# UI: показ топ-3 и валидация пользователем
# -------------------------
def show_top_and_validate(top_candidates: List[Tuple[float, Dict, Dict]]):
    """
    Показывает топ-3 и запрашивает валидацию от пользователя.
    """
    print("\n=== TOP-3 КАНДИДАТОВ (ПОРТФЕЛИ) ===")
    shortlist = top_candidates[:3]
    for i, (score, portfolio, heur) in enumerate(shortlist, start=1):
        print(f"\n[{i}] Score: {score:.2f}")
        print(json.dumps(portfolio, ensure_ascii=False, indent=2))

        # #[ИЗ RAW]: попросить LLM дать краткий анализ
        meta = {"weights": WEIGHTS}
        explain = explain_portfolio_strategy(portfolio, meta)
        print("LLM Analysis:", json.dumps(explain, ensure_ascii=False, indent=2))

        print("\n--- Оцените кандидата: '+' сохранить направление, '-' заменить/изменить ---")
        # В DEMO_MODE пропускаем ручной ввод, чтобы скрипт не зависал при автоматическом тестировании
        if DEMO_MODE:
            print("[DEMO MODE] Автоматическая оценка: '+'")
            raw = "+"
        else:
            while True:
                raw = input("Оценка (+ / -): ").strip()
                if raw in ["+", "-"]:
                    break
                print("Ожидается '+' или '-'")
        portfolio["_validator_vote"] = raw

    return shortlist


# -------------------------
# MAIN: запуск пайплайна
# -------------------------
def main():
    print("[*] Инициализация Эволюционного Движка...")

    # #[ДОБАВЛЕНО]: Генерация Mock-данных для DEMO_MODE, чтобы скрипт работал "из коробки"
    # В реальном проекте здесь будет загрузка из data/normalized/
    # #[ИЗМЕНЕНО]: Расширен набор Mock-данных для адекватной симуляции эволюции
    mock_graph = [
        {"id": "1", "name": "Tech Sector", "stats": [], "is_core_market": True},
        {"id": "2", "name": "Emerging Markets", "stats": [], "is_core_market": True},
        {"id": "3", "name": "Energy Sector", "stats": [], "is_core_market": False},
        {"id": "4", "name": "Real Estate", "stats": [], "is_core_market": False},
        {"id": "5", "name": "Bonds & Treasuries", "stats": [], "is_core_market": False},
        {"id": "6", "name": "Precious Metals", "stats": [], "is_core_market": False}
    ]
    mock_primary = [
        {"id": "A1", "name": "AAPL", "tags": ["Equities"]},
        {"id": "A2", "name": "BTC", "tags": ["Crypto", "HFT"]},
        {"id": "A3", "name": "NVDA", "tags": ["Equities", "AI"]},
        {"id": "A4", "name": "ETH", "tags": ["Crypto"]},
        {"id": "A5", "name": "US10Y", "tags": ["Bonds"]}
    ]
    mock_derivs = [
        {"id": "D1", "name": "Call Option", "tags": ["Derivative"]},
        {"id": "D2", "name": "Futures Contract", "tags": ["Derivative"]},
        {"id": "D3", "name": "Put Option", "tags": ["Derivative", "Hedge"]},
        {"id": "D4", "name": "Perpetual Swap", "tags": ["Derivative", "Crypto"]}
    ]
    mock_rules = {"max_active": 5, "slots": {"equities": 1, "crypto": 1}}

    print(
        f"[*] Пул активов: {len(mock_primary)} базовых, {len(mock_derivs)} деривативов, узлов графа: {len(mock_graph)}")
    print("[*] Запуск эволюции (Генетический алгоритм)...")

    top = evolve_portfolios(mock_primary, mock_derivs, mock_graph, mock_rules)

    # Выбираем топ-3 для показа/валидации
    top3 = top[:3]
    validated = show_top_and_validate(top3)

    plus_count = sum(1 for s, b, h in validated if b.get("_validator_vote") == "+")
    minus_count = sum(1 for s, b, h in validated if b.get("_validator_vote") == "-")
    print(f"\n[*] Валидация завершена: + = {plus_count}, - = {minus_count}")

    main_portfolio = None
    alternatives = []
    for sc, bld, h in top:
        if bld.get("_validator_vote") == "+" and main_portfolio is None:
            main_portfolio = (sc, bld, h)
    if not main_portfolio:
        main_portfolio = top[0]

    for sc, bld, h in top:
        if (sc, bld, h) != main_portfolio:
            alternatives.append((sc, bld, h))
        if len(alternatives) >= 2:
            break

    print("\n=== ФИНАЛЬНЫЙ РЕЗУЛЬТАТ ===")
    print("Основной портфель:")
    print(json.dumps(main_portfolio[1], ensure_ascii=False, indent=2))
    print("Альтернативы:")
    for alt in alternatives:
        print(json.dumps(alt[1], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()