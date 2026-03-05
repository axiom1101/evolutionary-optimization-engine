import argparse
import sys
import os
import configparser

# Читаем конфиг для отображения статуса при запуске
config_path = os.path.join(os.path.dirname(__file__), 'configs', 'settings.ini')
config = configparser.ConfigParser()
config.read(config_path)
DEMO_MODE = config.getboolean('DEFAULT', 'DEMO_MODE', fallback=True)


def print_banner():
    print("=" * 50)
    print(" 🧬 EOE: Evolutionary Optimization Engine")
    print(f" ⚙️  DEMO_MODE: {'[ON] Safe Execution' if DEMO_MODE else '[OFF] Production'}")
    print("=" * 50)


def run_etl():
    print("[*] Запуск ETL пайплайна (Ingestion Layer)...")

    # #[ДОБАВЛЕНО]: Вызов нашего нового парсера
    from ingestion.legacy_parser import process_file_etl

    print("\n[ETL] Старт обработки Legacy-конфигураций...")
    # Имитируем обработку файла (в DEMO_MODE он сгенерирует mock-файл)
    process_file_etl(input_filename="market_data_dump.lua", output_filename="market_data_normalized.json")

    print("\n[ETL] Пайплайн успешно завершен. Данные готовы для In-Memory индексов.")


def run_agent(custom_query=None):
    print("[*] Запуск AI-Агента (NLP Pipeline & LLM Orchestration)...")

    from agents.intent_router import IntentRouter
    from agents.response_formatter import ResponseFormatter

    router = IntentRouter()
    formatter = ResponseFormatter()

    # #[ДОБАВЛЕНО]: Интерактивный ввод, если запрос не передан через аргументы
    if custom_query:
        user_query = custom_query
    else:
        print("\n[?] Введите ваш запрос (или нажмите Enter для тестового):")
        user_query = input(">>> ").strip()
        if not user_query:
            user_query = "Сделай мне агрессивный портфель на т1 с волатильным рынком"

    print(f"\n[USER]: {user_query}")

    routed_data = router.route_query(user_query)
    print(f"[ROUTER]: Распознан интент -> {routed_data['intent']}")
    print(f"[ROUTER]: Извлечены параметры -> {routed_data['parameters']}")

    mock_search_results = {
        "core_assets": [{"name": "BTC/USDT"}, {"name": "ETH/USDT"}],
        "derivatives": [{"name": "BTC-PERP-Options"}],
        "bonds": [{"type": "US Treasuries"}]
    }

    print("\n[*] Форматирование отчета...")
    final_report = formatter.format_response(routed_data, mock_search_results)
    print(f"\n[SYSTEM RESPONSE]:\n{final_report}")

    if routed_data['intent'] == "unknown":
        from agents.llm_client import ask_ollama
        print("\n[*] Интент не распознан. Передача запроса в LLM (Fallback)...")
        llm_response = ask_ollama(
            system_prompt="Ты финансовый AI-ассистент. Отвечай коротко.",
            user_prompt=user_query
        )
        print(f"[LLM RESPONSE]:\n{llm_response}")


def run_evolution():
    print("[*] Запуск Генетического Алгоритма (Core Engine)...")
    # Здесь позже будет вызов core.evolution_engine.main()
    print("[-] Модуль Эволюции пока в разработке.")


def main():
    print_banner()

    parser = argparse.ArgumentParser(description="EOE Command Line Interface")
    parser.add_argument('--etl', action='store_true', help='Запустить сбор и нормализацию данных')
    # #[ИЗМЕНЕНО]: Теперь --agent может принимать строку
    parser.add_argument('--agent', nargs='?', const=True,
                        help='Запустить AI-Агента. Можно передать текст запроса в кавычках.')
    parser.add_argument('--evolve', action='store_true', help='Запустить генетический алгоритм')

    args = parser.parse_args()

    if args.etl:
        run_etl()
    elif args.agent is not None:
        # Если передали текст, args.agent будет строкой. Если просто флаг - True.
        query = args.agent if isinstance(args.agent, str) else None
        run_agent(query)
    elif args.evolve:
        run_evolution()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()