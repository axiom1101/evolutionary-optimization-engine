# 📘 Runbook: RPA & Computer Vision (Signal Monitor)

This module demonstrates the use of Robotic Process Automation (RPA) and Computer Vision to interact with legacy trading terminals or systems that lack a dedicated API.

## ⚙️ Prerequisites
If running in Production Mode (`DEMO_MODE = False`), ensure the following libraries are installed:
```bash
pip install pyautogui pynput pygetwindow opencv-python
```
*Note: In `DEMO_MODE = True`, the script safely simulates the detection loop without taking control of your mouse, ensuring safe execution during CI/CD or code reviews.*

## 🚀 CLI Usage
Run the script with the `--rpa` flag:
```bash
python main.py --rpa
```

## 🧠 Expected Behavior
1. **Window Hooking:** The script attempts to find and bring the target application (e.g., "Trading Terminal") to the foreground.
2. **Pattern Matching:** It continuously scans the screen for a specific visual trigger (`assets/trade_signal_indicator.png`) using OpenCV template matching.
3. **Anti-Bot Evasion:** When a signal is detected, it calculates a randomized click coordinate within the bounding box and applies randomized mouse movement duration and click delays to simulate human behavior.