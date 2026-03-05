import os
import json
import subprocess
import configparser

# #[ДОБАВЛЕНО]: Чтение конфигурации из единого файла settings.ini для поддержки DEMO_MODE
config_path = os.path.join(os.path.dirname(__file__), '..', 'configs', 'settings.ini')
config = configparser.ConfigParser()
config.read(config_path)

DEMO_MODE = config.getboolean('DEFAULT', 'DEMO_MODE', fallback=True)
GEMINI_API_KEY = config.get('API', 'GEMINI_API_KEY', fallback='')
OLLAMA_MODEL = config.get('MODELS', 'OLLAMA_DEFAULT_MODEL', fallback='mistral-7b-q4_K_M')
GEMINI_MODEL = config.get('MODELS', 'GEMINI_DEFAULT_MODEL', fallback='gemini-2.0-flash')


# #[ИЗ RAW]:
# def load_config(file_path):
#     with open(file_path, 'r', encoding='utf-8') as f:
#         return f.read().strip()
# API_KEY = load_config('api_key.txt')
# #[УДАЛЕНО]: Самописная функция load_config и хардкод 'api_key.txt'.
# Заменено на стандартный configparser для безопасности и удобства.


def ask_ollama(system_prompt: str, user_prompt: str, model: str = OLLAMA_MODEL) -> str:
    """
    Вызов локальной модели Ollama через CLI.
    """
    # #[ДОБАВЛЕНО]: Перехват вызова в демо-режиме (Правило 3)
    if DEMO_MODE:
        print(f"[DEMO MODE] Перехват вызова Ollama (модель: {model})")
        return json.dumps({
            "status": "success",
            "message": "Это mock-ответ от Ollama. Реальный вызов отключен флагом DEMO_MODE."
        }, ensure_ascii=False)

    # #[ИЗ RAW]:
    # def ollama_generate(system_prompt: str, user_prompt: str, model: str="mistral-7b-q4_K_M", max_tokens: int=256) -> str:
    #     cmd =["ollama", "generate", model, "--system", system_prompt, "--prompt", user_prompt, "--max-tokens", str(max_tokens)]
    #     process = subprocess.run(cmd, capture_output=True, text=True)
    # #[ИЗМЕНЕНО]: Оставили твой процедурный вызов через subprocess. Это надежно и не требует
    # установки дополнительных python-библиотек (типа библиотеки ollama), нужен только сам бинарник.

    cmd = [
        "ollama", "generate", model,
        "--system", system_prompt,
        "--prompt", user_prompt
    ]

    try:
        process = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return process.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Ошибка вызова Ollama: {e.stderr}")


def ask_gemini(system_prompt: str, user_prompt: str, image_path: str = None) -> str:
    """
    Вызов облачной модели Gemini (с поддержкой Vision).
    """
    # #[ДОБАВЛЕНО]: Перехват вызова в демо-режиме (Правило 3)
    if DEMO_MODE:
        print("[DEMO MODE] Перехват вызова Gemini API")
        return json.dumps({
            "verdict": "JACKPOT",
            "price": "50 chaos",
            "reason": "Mock-ответ для тестирования пайплайна без траты токенов API."
        }, ensure_ascii=False)

    # #[ИЗ RAW]:
    # client = genai.Client(api_key=API_KEY)
    # response = client.models.generate_content(model=MODEL_ID, contents=[SYSTEM_PROMPT, img])
    # #[ИЗМЕНЕНО]: Изолировали логику вызова в отдельную функцию. Импорты библиотек
    # google.genai и PIL спрятаны внутрь функции, чтобы скрипт не падал при старте,
    # если эти библиотеки не установлены (особенно полезно для DEMO_MODE).

    from google import genai
    from PIL import Image

    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY не найден в settings.ini")

    client = genai.Client(api_key=GEMINI_API_KEY)
    contents = [system_prompt, user_prompt]

    if image_path and os.path.exists(image_path):
        img = Image.open(image_path)
        contents.append(img)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents
    )

    return response.text