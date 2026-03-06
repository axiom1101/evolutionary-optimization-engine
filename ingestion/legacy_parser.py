import os
import re
import json

# #[ДОБАВЛЕНО]: Импорт конфига для соблюдения архитектуры
import configparser

config_path = os.path.join(os.path.dirname(__file__), '..', 'configs', 'settings.ini')
config = configparser.ConfigParser()
config.read(config_path)
DEMO_MODE = config.getboolean('DEFAULT', 'DEMO_MODE', fallback=True)

# #[ИЗ RAW]: Блок try-except для импорта slpp и создания парсера
try:
    import slpp

    if hasattr(slpp, 'SLPP'):
        _SLPP_PARSER_INSTANCE = slpp.SLPP()


        # #[ИЗ RAW]: def parse_lua_table(lua_str):
        # #[ИЗМЕНЕНО]: Добавлены Type Hints и Docstrings
        def parse_legacy_config(raw_str: str) -> dict:
            """
            Парсит неструктурированную Lua-подобную строку (Legacy Config)
            и возвращает Python-словарь.
            """
            try:
                processed_str = re.sub(r'^\s*return\s*', '', raw_str, flags=re.IGNORECASE)

                first_brace = processed_str.find("{")
                if first_brace != -1:
                    processed_str = processed_str[first_brace:]

                processed_str = re.sub(r'--.*$', '', processed_str, flags=re.MULTILINE)
                processed_str = re.sub(r',(\s*[}\]])', r'\1', processed_str)
                processed_str = re.sub(r'(\s*=\s*)-(\s*[,}])', r'\1nil\2', processed_str)
                processed_str = re.sub(r'-(\s*[,}])', r'0\1', processed_str)
                processed_str = processed_str.strip()

                parsed_data = _SLPP_PARSER_INSTANCE.decode(processed_str)

                if isinstance(parsed_data, list) and len(parsed_data) == 1 and isinstance(parsed_data[0], dict):
                    parsed_data = parsed_data[0]

                return parsed_data
            except Exception as e:
                print(f"[ERROR] Ошибка лексического анализатора: {e}")
                raise e
    else:
        def parse_legacy_config(raw_str: str) -> dict:
            raise ImportError("slpp установлен, но не содержит SLPP класс.")

except ImportError:
    slpp = None
    print("[WARNING] Библиотека 'slpp' не найдена. ETL-пайплайн будет работать в ограниченном режиме.")


    def parse_legacy_config(raw_str: str) -> dict:
        raise ImportError("slpp не установлен. Выполните: pip install slpp")


# #[ДОБАВЛЕНО]: Функция-обертка для полноценного ETL-процесса (Extract -> Transform -> Load)
def process_file_etl(input_filename: str, output_filename: str):
    """
    Читает сырой файл из data/raw/, парсит его и сохраняет JSON в data/normalized/.
    """
    base_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    raw_path = os.path.join(base_dir, 'raw', input_filename)
    norm_path = os.path.join(base_dir, 'normalized', output_filename)

    if not os.path.exists(raw_path):
        # #[ДОБАВЛЕНО]: Заглушка для DEMO_MODE, чтобы скрипт не падал, если файла нет
        if DEMO_MODE:
            print(f"[DEMO MODE] Файл {input_filename} не найден. Создаю mock-данные.")
            mock_data = {"status": "success", "source": "demo_mock", "items": [1, 2, 3]}
            os.makedirs(os.path.dirname(norm_path), exist_ok=True)
            with open(norm_path, 'w', encoding='utf-8') as f:
                json.dump(mock_data, f, indent=2)
            print(f"[+] Mock-данные сохранены в {norm_path}")
            return
        else:
            print(f"[ERROR] Файл не найден: {raw_path}")
            return

    print(f"[*] Extracting: Чтение {input_filename}...")
    with open(raw_path, 'r', encoding='utf-8') as f:
        raw_content = f.read()

    print(f"[*] Transforming: Очистка и лексический анализ...")
    parsed_dict = parse_legacy_config(raw_content)

    print(f"[*] Loading: Сохранение нормализованного JSON...")
    os.makedirs(os.path.dirname(norm_path), exist_ok=True)
    with open(norm_path, 'w', encoding='utf-8') as f:
        json.dump(parsed_dict, f, ensure_ascii=False, indent=2)

    print(f"[+] Успешно! Файл сохранен: {norm_path}")


if __name__ == "__main__":
    # Локальный тест модуля
    process_file_etl("test_config.lua", "test_config.json")