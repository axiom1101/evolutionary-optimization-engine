from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class ModifierType(Enum):
    BASE = "BASE"  # Базовое значение (например, стартовый капитал или базовый риск)
    INC = "INC"  # Аддитивный модификатор (например, фиксированные бонусы/комиссии)
    MORE = "MORE"  # Мультипликативный модификатор (например, кредитное плечо, сложный процент)


# #[ИЗ RAW]: class Mod:
@dataclass
class MetricModifier:
    """Представляет один финансовый или системный модификатор."""
    metric_name: str  # Бывший 'type' (например, "ExpectedYield", "MaxDrawdown")
    key: ModifierType  # BASE, INC, MORE
    value: float  # Значение модификатора
    source: str = "Unknown"
    condition: str = ""


# #[ИЗ RAW]: class ModDB:
class MetricsDB:
    """Класс для хранения и агрегации сложных метрик портфеля/системы."""

    def __init__(self):
        # Словарь: { "имя_метрики":[список_объектов_MetricModifier] }
        self.modifiers: Dict[str, List[MetricModifier]] = {}

    def add_modifier(self, metric_name: str, mod_key: ModifierType, value: float, source: str = "Unknown",
                     condition: str = ""):
        """Добавляет модификатор в базу."""
        if metric_name not in self.modifiers:
            self.modifiers[metric_name] = []
        self.modifiers[metric_name].append(MetricModifier(metric_name, mod_key, value, source, condition))

    # #[ИЗ RAW]: def add_mod_from_dict(self, mod_dict: Dict[str, Any]):
    def add_modifier_from_dict(self, mod_dict: Dict[str, Any]):
        """Добавляет модификатор из словаря (результата парсера)."""
        metric_name = mod_dict.get("type")  # В RAW это называлось type
        mod_key_str = mod_dict.get("key")
        value = mod_dict.get("value")
        source = mod_dict.get("source", "Unknown")
        condition = mod_dict.get("condition", "")

        if metric_name and mod_key_str and value is not None:
            try:
                mod_key = ModifierType(mod_key_str)
                self.add_modifier(metric_name, mod_key, value, source, condition)
            except ValueError:
                print(f"[WARNING] Неизвестный тип модификатора: {mod_key_str}. Пропуск.")
        else:
            print(f"[WARNING] Неполный словарь модификатора: {mod_dict}")

    # #[ИЗ RAW]: def sum_mods(self, mod_type: str) -> float:
    def calculate_total_metric(self, metric_name: str) -> float:
        """
        Агрегирует модификаторы заданного типа по правилам BASE/INC/MORE.
        Возвращает итоговое значение метрики.
        """
        mods_of_type = self.modifiers.get(metric_name, [])
        if not mods_of_type:
            return 0.0

        base_val = 0.0
        inc_val = 0.0
        more_val = 1.0  # MORE модификаторы перемножаются

        for mod in mods_of_type:
            if mod.key == ModifierType.BASE:
                base_val += mod.value
            elif mod.key == ModifierType.INC:
                inc_val += mod.value
            elif mod.key == ModifierType.MORE:
                # #[ИЗ RAW]: more_val *= (1 + mod.value / 100)
                more_val *= (1 + mod.value / 100)

        # #[ИЗ RAW]: total_val = (base_val + inc_val) * more_val
        # Формула: (База + Аддитивные бонусы) * Мультипликаторы (Плечо)
        total_val = (base_val + inc_val) * more_val
        return total_val

    # #[ИЗ RAW]: def flag_mods(self, mod_type: str) -> bool:
    def has_flag(self, metric_name: str) -> bool:
        """
        Проверяет, есть ли хотя бы один модификатор-флаг (например, "IsHedgingActive").
        """
        mods_of_type = self.modifiers.get(metric_name, [])
        return len(mods_of_type) > 0


# --- Тестирование ---
if __name__ == "__main__":
    print("--- Тестирование core/metrics_db.py ---")
    db = MetricsDB()

    # #[ИЗ RAW]: mod_db.add_mod("Life", ModType.BASE, 50, source="Jewel")
    # #[ИЗМЕНЕНО]: Демонстрация финансовой математики

    # 1. Считаем Капитал (Capital)
    db.add_modifier("Capital", ModifierType.BASE, 1000, source="Initial Deposit")
    db.add_modifier("Capital", ModifierType.BASE, 500, source="Investor A")
    db.add_modifier("Capital", ModifierType.INC, 10, source="Sign-up Bonus")  # +10% к базе
    db.add_modifier("Capital", ModifierType.MORE, 50, source="Margin Leverage 1.5x")  # Умножаем итог на 1.5

    total_capital = db.calculate_total_metric("Capital")
    print(f"Итоговый Капитал: ${total_capital}")  # (1500 + 150) * 1.5 = 2475.0

    # 2. Считаем Риск (Drawdown)
    db.add_modifier("Drawdown", ModifierType.BASE, 5, source="Market Volatility")
    db.add_modifier("Drawdown", ModifierType.INC, 2, source="High-Risk Asset")

    total_drawdown = db.calculate_total_metric("Drawdown")
    print(f"Итоговая просадка (Риск): {total_drawdown}%")  # 5 + 2 = 7.0

    # 3. Проверяем флаги
    db.add_modifier("IsHedgingActive", ModifierType.BASE, 1, source="Options Contract")
    is_hedged = db.has_flag("IsHedgingActive")
    print(f"Хеджирование активно: {is_hedged}")  # True

    print("--- Тестирование завершено ---")