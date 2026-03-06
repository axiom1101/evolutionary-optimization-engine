import os
import json
from typing import Dict, List, Any, Optional


# #[ИЗ RAW]: class DBSearch:
# #[ИЗМЕНЕНО]: Переименовано в InMemoryIndex. Логика инвертированных индексов сохранена.
class InMemoryIndex:
    """
    Модуль для In-Memory индексации и быстрого поиска по нормализованным данным.
    Использует инвертированные индексы для обеспечения субмиллисекундных задержек.
    """

    def __init__(self, data_path: str = "data/normalized", parser_instance=None):
        self.data_path = data_path
        self.parser = parser_instance

        # --- Индексы для поиска ---
        # #[ИЗ RAW]: self._item_mod_index, self._gem_tag_index, self._passive_mod_index
        # #[ИЗМЕНЕНО]: Рескин под финансовые инструменты
        self._asset_metric_index: Dict[str, List[Dict[str, Any]]] = {}
        self._derivative_tag_index: Dict[str, List[Dict[str, Any]]] = {}
        self._node_correlation_index: Dict[str, List[Dict[str, Any]]] = {}
        self._asset_type_index: Dict[str, List[Dict[str, Any]]] = {}

        # --- Данные ---
        self.assets_data: Dict[str, Any] = {}
        self.derivatives_data: Dict[str, Any] = {}
        self.graph_data: Dict[str, Any] = {}

        self._build_indexes()

    def _build_indexes(self):
        """
        Создаёт индексы для быстрого поиска.
        Вызывается при инициализации или после загрузки новых данных.
        """
        print("[*] Построение In-Memory индексов...")

        # 1. Индексация базовых активов (бывшие items)
        for asset_name, asset_props in self.assets_data.items():
            asset_type = asset_props.get("type")
            if asset_type:
                if asset_type not in self._asset_type_index:
                    self._asset_type_index[asset_type] = []
                self._asset_type_index[asset_type].append(asset_props)

            # Индекс по метрикам (бывшие моды)
            all_metrics = asset_props.get("implicit_metrics", []) + asset_props.get("explicit_metrics", [])
            for metric_dict in all_metrics:
                metric_type = metric_dict.get("type")  # e.g., "Volatility", "Yield"
                if metric_type:
                    if metric_type not in self._asset_metric_index:
                        self._asset_metric_index[metric_type] = []
                    indexed_asset = asset_props.copy()
                    indexed_asset["_metric"] = metric_dict
                    self._asset_metric_index[metric_type].append(indexed_asset)

        # 2. Индексация деривативов (бывшие gems)
        for deriv_name, deriv_props in self.derivatives_data.items():
            tags = deriv_props.get("tags", [])
            for tag in tags:
                if tag not in self._derivative_tag_index:
                    self._derivative_tag_index[tag] = []
                self._derivative_tag_index[tag].append(deriv_props)

        # 3. Индексация узлов графа (бывшие passives/tree)
        graph_nodes = self.graph_data.get("nodes", {})
        for node_id, node_props in graph_nodes.items():
            node_stats = node_props.get("stats", [])
            for stat_dict in node_stats:
                stat_type = stat_dict.get("type")
                if stat_type:
                    if stat_type not in self._node_correlation_index:
                        self._node_correlation_index[stat_type] = []
                    indexed_node = node_props.copy()
                    indexed_node["_metric"] = stat_dict
                    indexed_node["_node_id"] = node_id
                    self._node_correlation_index[stat_type].append(indexed_node)

        print("[+] Индексы успешно построены.")

    # #[ИЗ RAW]: def load_data(self, items_data, gems_data, tree_data):
    def load_data(self, assets_data: Optional[Dict[str, Any]] = None,
                  derivatives_data: Optional[Dict[str, Any]] = None,
                  graph_data: Optional[Dict[str, Any]] = None):
        """
        Загружает данные из Data Lake и перестраивает индексы.
        """
        if assets_data is not None: self.assets_data = assets_data
        if derivatives_data is not None: self.derivatives_data = derivatives_data
        if graph_data is not None: self.graph_data = graph_data

        self._asset_metric_index.clear()
        self._derivative_tag_index.clear()
        self._node_correlation_index.clear()
        self._asset_type_index.clear()
        self._build_indexes()

    # --- ПУБЛИЧНЫЕ МЕТОДЫ ПОИСКА (O(1) Complexity) ---

    # #[ИЗ RAW]: def search_items_by_mod(self, mod_type: str) -> List[Dict[str, Any]]:
    def search_assets_by_metric(self, metric_type: str) -> List[Dict[str, Any]]:
        return self._asset_metric_index.get(metric_type, [])

    # #[ИЗ RAW]: def search_gems_by_tag(self, tag: str) -> List[Dict[str, Any]]:
    def search_derivatives_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        return self._derivative_tag_index.get(tag, [])

    # #[ИЗ RAW]: def search_passives_by_mod(self, mod_type: str) -> List[Dict[str, Any]]:
    def search_nodes_by_correlation(self, correlation_type: str) -> List[Dict[str, Any]]:
        return self._node_correlation_index.get(correlation_type, [])

    def search_assets_by_type(self, asset_type: str) -> List[Dict[str, Any]]:
        return self._asset_type_index.get(asset_type, [])


# --- Тестирование ---
if __name__ == "__main__":
    print("--- Тестирование core/in_memory_index.py ---")

    index = InMemoryIndex()

    # Имитация нормализованных данных из Data Lake
    example_assets = {
        "BTC_Spot": {
            "type": "Crypto",
            "implicit_metrics": [{"type": "Volatility", "value": "High"}],
            "explicit_metrics": [{"type": "Yield", "value": "15%"}]
        },
        "US_Treasury": {
            "type": "Bonds",
            "implicit_metrics": [],
            "explicit_metrics": [{"type": "Yield", "value": "4%"}, {"type": "SafeHaven", "value": "True"}]
        }
    }
    example_derivatives = {
        "BTC_Call_Option": {
            "name": "BTC_Call_Option",
            "tags": ["crypto", "options", "high_risk"]
        },
        "SP500_Futures": {
            "name": "SP500_Futures",
            "tags": ["equities", "futures", "hedge"]
        }
    }
    example_graph = {
        "nodes": {
            "Node_1": {"name": "Tech Sector Correlation", "stats": [{"type": "TechExposure"}]},
            "Node_2": {"name": "Inflation Hedge", "stats": [{"type": "SafeHaven"}]}
        }
    }

    print("\n[*] Загрузка данных в In-Memory Index...")
    index.load_data(assets_data=example_assets, derivatives_data=example_derivatives, graph_data=example_graph)

    print("\n--- Результаты мгновенного поиска ---")

    yield_assets = index.search_assets_by_metric("Yield")
    print(f"Активы с метрикой 'Yield': {len(yield_assets)} найдено")
    for a in yield_assets:
        print(f"  - {a.get('type')} (Метрика: {a.get('_metric')})")

    crypto_derivs = index.search_derivatives_by_tag("crypto")
    print(f"\nДеривативы с тегом 'crypto': {len(crypto_derivs)} найдено")
    for d in crypto_derivs:
        print(f"  - {d.get('name')}")

    safe_nodes = index.search_nodes_by_correlation("SafeHaven")
    print(f"\nУзлы графа с корреляцией 'SafeHaven': {len(safe_nodes)} найдено")
    for n in safe_nodes:
        print(f"  - {n.get('name')} (ID: {n.get('_node_id')})")

    print("\n--- Тестирование завершено ---")