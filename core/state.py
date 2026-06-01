# core/state.py — obsługa stanu pozycji per symbol (binance-bot3)

import json
import os


def _state_file_path(symbol: str) -> str:
    """Zwraca ścieżkę do pliku stanu dla danego symbolu."""
    return f"state/{symbol.lower()}_state.json"


def load_position_state(symbol: str) -> dict:
    """
    Wczytuje stan pozycji dla symbolu.
    Jeśli plik nie istnieje — zwraca pusty stan.
    """
    path = _state_file_path(symbol)

    if not os.path.exists(path):
        return {
            "position": None,        # "LONG" lub None
            "entry_price": None,
            "sl": None,
            "tp": None,
            "ts_active": False,
        }

    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        # Jeśli plik jest uszkodzony — resetujemy stan
        return {
            "position": None,
            "entry_price": None,
            "sl": None,
            "tp": None,
            "ts_active": False,
        }


def save_position_state(symbol: str, state: dict):
    """
    Zapisuje stan pozycji do pliku JSON.
    """
    path = _state_file_path(symbol)

    with open(path, "w") as f:
        json.dump(state, f, indent=2)
