import os
import random
import time
import configparser

# #[ДОБАВЛЕНО]: Чтение конфига для безопасного запуска
config_path = os.path.join(os.path.dirname(__file__), '..', 'configs', 'settings.ini')
config = configparser.ConfigParser()
config.read(config_path)
DEMO_MODE = config.getboolean('DEFAULT', 'DEMO_MODE', fallback=True)

# #[ИЗ RAW]: Импорты библиотек автоматизации
try:
    import pyautogui
    from pynput import keyboard
    import pygetwindow as gw

    LIBRARIES_INSTALLED = True
except ImportError:
    LIBRARIES_INSTALLED = False
    if not DEMO_MODE:
        print("[WARNING] Библиотеки pyautogui, pynput или pygetwindow не установлены.")

# -------------------------
# Настройки RPA-Агента
# -------------------------
# #[ИЗ RAW]: IMAGE_PATH = 'target_clean.png'
# #[ИЗМЕНЕНО]: Рескин под финансовый индикатор
IMAGE_PATH = 'assets/trade_signal_indicator.png'
# #[ИЗ RAW]: WINDOW_TITLE = "Chrome"
WINDOW_TITLE = "Trading Terminal"
DELAY_BEFORE_START = 3
CLICKS_PER_FIND = 1
MIN_CLICK_DELAY = 0.5
MAX_CLICK_DELAY = 3.0
MIN_PRESS_DURATION = 0.05
MAX_PRESS_DURATION = 0.3
CONFIDENCE = 0.8
GRAYSCALE = True

stop_flag = False


def on_press(key):
    global stop_flag
    if hasattr(key, 'char') and key.char == 'q':
        stop_flag = True
        print("\n[!] Получен сигнал остановки (нажата 'q'). Завершение цикла...")
        return False


def run_monitor():
    global stop_flag
    print("=" * 50)
    print(" 🤖 EOE: RPA & Computer Vision Signal Monitor")
    print("=" * 50)

    if DEMO_MODE:
        print("[DEMO MODE] Включен режим безопасной симуляции.")
        print("[DEMO MODE] Реальное управление мышью ОТКЛЮЧЕНО для безопасности хоста.")
        print(f"[*] Ожидание {DELAY_BEFORE_START} сек. перед стартом...")
        time.sleep(DELAY_BEFORE_START)

        print(f"[*] Поиск окна '{WINDOW_TITLE}'...")
        time.sleep(1)
        print(f"[+] Окно '{WINDOW_TITLE}' успешно привязано (Mock).")

        print(f"[*] Сканирование экрана на наличие паттерна '{IMAGE_PATH}'... (Нажмите Ctrl+C для выхода)")
        try:
            for i in range(3):
                time.sleep(random.uniform(1.0, 2.5))
                mock_x, mock_y = random.randint(100, 800), random.randint(100, 600)
                print(f"[+] Сигнал обнаружен! Эмуляция клика в координатах ({mock_x}, {mock_y})")
                print(
                    f"    -> Задержка исполнения: {random.uniform(MIN_PRESS_DURATION, MAX_PRESS_DURATION):.3f}s (Anti-Bot Evasion)")
            print("\n[!] Демонстрационный цикл завершен.")
        except KeyboardInterrupt:
            print("\n[!] Остановка монитора.")
        return

    if not LIBRARIES_INSTALLED:
        print(
            "[ERROR] Для работы в Production-режиме установите зависимости: pip install pyautogui pynput pygetwindow opencv-python")
        return

    # --- PRODUCTION РЕЖИМ (Оригинальный код из RAW) ---
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    print(f"[*] Запуск RPA-агента. Старт через {DELAY_BEFORE_START} секунд...")
    time.sleep(DELAY_BEFORE_START)

    windows = gw.getWindowsWithTitle(WINDOW_TITLE)
    if windows:
        target_window = windows[0]
        target_window.activate()
        print(f"[+] Активировано окно терминала: '{target_window.title}'")
        time.sleep(0.5)
    else:
        print(f"[-] Окно с названием '{WINDOW_TITLE}' не найдено. Переход в фоновый режим.")

    print(f"[*] Начинаю сканирование '{IMAGE_PATH}'... Нажмите 'q' для остановки.")

    try:
        while not stop_flag:
            try:
                location = pyautogui.locateOnScreen(IMAGE_PATH, confidence=CONFIDENCE, grayscale=GRAYSCALE)
            except Exception as e:
                print(f"[-] Ошибка CV-модуля: {e}")
                location = None

            if location:
                x, y, width, height = location
                center_x, center_y = x + width // 2, y + height // 2

                # #[ИЗ RAW]: Рандомное смещение внутри найденной области (человеческая неточность)
                offset_x = random.randint(-width // 4, width // 4)
                offset_y = random.randint(-height // 4, height // 4)
                click_x, click_y = center_x + offset_x, center_y + offset_y

                print(f"[+] Торговый сигнал найден! Исполнение ордера в ({click_x}, {click_y})")

                for _ in range(CLICKS_PER_FIND):
                    pyautogui.moveTo(click_x, click_y, duration=random.uniform(0.1, 0.4))
                    press_duration = random.uniform(MIN_PRESS_DURATION, MAX_PRESS_DURATION)
                    pyautogui.mouseDown()
                    time.sleep(press_duration)
                    pyautogui.mouseUp()

                    if _ < CLICKS_PER_FIND - 1:
                        time.sleep(random.uniform(0.1, 0.5))

                next_delay = random.uniform(MIN_CLICK_DELAY, MAX_CLICK_DELAY)
                print(f"[*] Ожидание {next_delay:.2f} сек. до следующего сканирования...")
                time.sleep(next_delay)
            else:
                time.sleep(1)

    except KeyboardInterrupt:
        print("\n[!] Прервано пользователем (Ctrl+C).")
    finally:
        listener.stop()
        print("[*] Работа RPA-агента завершена.")


if __name__ == "__main__":
    run_monitor()