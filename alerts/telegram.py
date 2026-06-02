# alerts/telegram.py — v0.1.3
# Anti-spam, multi-user, jeden ostatni alert
# + pełne alerty BUY / SELL / START / ERROR

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

STATE_FILE = "state/telegram_state.json"
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


# ─────────────────────────────────────────────
#  Obsługa stanu (anti-spam)
# ─────────────────────────────────────────────

def _load_state():
    """Wczytuje stan ostatnich wiadomości."""
    if not os.path.exists(STATE_FILE):
        return {
            "last_production_message_id": None,
            "last_system_message_id": None,
        }

    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {
            "last_production_message_id": None,
            "last_system_message_id": None,
        }


def _save_state(state):
    """Zapisuje stan wiadomości."""
    with open(STATE_FILE, "w") as f:
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
        pass  # jedyny try/except w module


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
#  Alert produkcyjny — tylko jeden ostatni
# ─────────────────────────────────────────────

def send_production_alert(text: str):
    """
    Alert produkcyjny:
    - wysyłany do wielu odbiorców (CHAT_IDS)
    - ale trzymamy tylko JEDEN ostatni alert
    """
    state = _load_state()
    last_id = state.get("last_production_message_id")

    # Usuń poprzedni alert u wszystkich odbiorców
    if last_id:
        for chat_id in TELEGRAM_CHAT_IDS:
            _delete_message(chat_id, last_id)

    # Wyślij nowy alert
    new_id = None
    for chat_id in TELEGRAM_CHAT_IDS:
        new_id = _send(chat_id, text)

    # Zapisz ID ostatniego alertu
    state["last_production_message_id"] = new_id
    _save_state(state)


# ─────────────────────────────────────────────
#  Alert systemowy — tylko jeden ostatni
# ─────────────────────────────────────────────

def send_system_alert(text: str):
    """
    Alert systemowy:
    - wysyłany tylko do admina
    - trzymamy tylko JEDEN ostatni alert systemowy
    """
    if not TELEGRAM_ADMIN_ID:
        return

    state = _load_state()
    last_id = state.get("last_system_message_id")

    # Usuń poprzedni alert systemowy
    if last_id:
        _delete_message(TELEGRAM_ADMIN_ID, last_id)

    # Wyślij nowy alert
    new_id = _send(TELEGRAM_ADMIN_ID, text)

    # Zapisz ID
    state["last_system_message_id"] = new_id
    _save_state(state)


# ─────────────────────────────────────────────
#  Alerty produkcyjne: BUY / SELL
# ─────────────────────────────────────────────

def send_buy_alert(symbol: str, price: float):
    """Alert BUY — multi-user + anti-spam."""
    text = fmt_buy(symbol, price)
    send_production_alert(text)


def send_sell_alert(symbol: str, price: float, pnl: float | None = None):
    """Alert SELL — multi-user + anti-spam."""
    text = fmt_sell(symbol, price, pnl)
    send_production_alert(text)


# ─────────────────────────────────────────────
#  Alerty systemowe: START / ERROR
# ─────────────────────────────────────────────

def send_start_alert(symbol: str, interval: str, mode: str):
    """Alert START — admin only + anti-spam."""
    text = fmt_start(symbol, interval, mode)
    send_system_alert(text)


def send_error_alert(symbol: str, error: Exception):
    """Alert ERROR — admin only + anti-spam."""
    text = fmt_error(symbol, str(error))
    send_system_alert(text)
