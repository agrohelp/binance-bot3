# v0.1.4 — multi-symbol anti-spam (commit test)

# Multi-symbol anti-spam
# Każdy symbol ma własny ostatni alert BUY/SELL
# START/ERROR pozostają wspólne (systemowe)
# ja drugi raz commit

import json
import os
import requests

from settings.setting import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_IDS,
    TELEGRAM_ADMIN_ID,
)

from alerts.formats import (
    fmt_buy,
    fmt_sell,
    fmt_system,
    fmt_error,
    fmt_start,
)

# Plik systemowy (START/ERROR)
STATE_FILE_SYSTEM = "state/telegram_state_system.json"

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


# ─────────────────────────────────────────────
#  Obsługa stanu (anti-spam)
# ─────────────────────────────────────────────

def _load_state(path: str):
    """Wczytuje stan z podanej ścieżki."""
    if not os.path.exists(path):
        return {
            "last_production_message_id": None,
            "last_system_message_id": None,
        }

    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return {
            "last_production_message_id": None,
            "last_system_message_id": None,
        }


def _save_state(path: str, state):
    """Zapisuje stan do podanej ścieżki."""
    with open(path, "w") as f:
        json.dump(state, f, indent=2)


# ─────────────────────────────────────────────
#  Funkcje pomocnicze
# ─────────────────────────────────────────────

def _delete_message(chat_id, message_id):
    """Usuwa poprzedni alert (jeśli istnieje)."""
    if not message_id:
        return

    try:
        requests.get(
            f"{BASE_URL}/deleteMessage",
            params={"chat_id": chat_id, "message_id": message_id},
            timeout=5,
        )
    except Exception:
        pass


def _send(chat_id, text):
    """Wysyła wiadomość i zwraca message_id."""
    try:
        r = requests.get(
            f"{BASE_URL}/sendMessage",
            params={"chat_id": chat_id, "text": text},
            timeout=5,
        ).json()

        return r.get("result", {}).get("message_id")
    except Exception:
        return None


# ─────────────────────────────────────────────
#  Alert produkcyjny — osobny plik per symbol
# ─────────────────────────────────────────────

def send_production_alert(symbol: str, text: str):
    """
    BUY/SELL — każdy symbol ma własny plik stanu:
    state/telegram_state_<SYMBOL>.json
    """
    state_file = f"state/telegram_state_{symbol}.json"
    state = _load_state(state_file)
    last_id = state.get("last_production_message_id")

    # Usuń poprzedni alert dla tego symbolu
    if last_id:
        for chat_id in TELEGRAM_CHAT_IDS:
            _delete_message(chat_id, last_id)

    # Wyślij nowy alert
    new_id = None
    for chat_id in TELEGRAM_CHAT_IDS:
        new_id = _send(chat_id, text)

    # Zapisz ID ostatniego alertu
    state["last_production_message_id"] = new_id
    _save_state(state_file, state)


# ─────────────────────────────────────────────
#  Alert systemowy — wspólny
# ─────────────────────────────────────────────

def send_system_alert(text: str):
    """
    START/ERROR — jeden ostatni alert systemowy (admin only)
    """
    if not TELEGRAM_ADMIN_ID:
        return

    state = _load_state(STATE_FILE_SYSTEM)
    last_id = state.get("last_system_message_id")

    if last_id:
        _delete_message(TELEGRAM_ADMIN_ID, last_id)

    new_id = _send(TELEGRAM_ADMIN_ID, text)

    state["last_system_message_id"] = new_id
    _save_state(STATE_FILE_SYSTEM, state)


# ─────────────────────────────────────────────
#  Alerty produkcyjne: BUY / SELL
# ─────────────────────────────────────────────

def send_buy_alert(symbol: str, price: float):
    text = fmt_buy(symbol, price)
    send_production_alert(symbol, text)


def send_sell_alert(symbol: str, price: float, pnl: float | None = None):
    text = fmt_sell(symbol, price, pnl)
    send_production_alert(symbol, text)


# ─────────────────────────────────────────────
#  Alerty systemowe: START / ERROR
# ─────────────────────────────────────────────

def send_start_alert(symbol: str, interval: str, mode: str):
    text = fmt_start(symbol, interval, mode)
    send_system_alert(text)


def send_error_alert(symbol: str, error: Exception):
    text = fmt_error(symbol, str(error))
    send_system_alert(text)
