# v0.1.5 — multi-symbol anti-spam + START STATUS PRO + polskie podsumowanie

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

STATE_FILE_SYSTEM = "state/telegram_state_system.json"
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


# ─────────────────────────────────────────────
#  Obsługa stanu (anti-spam)
# ─────────────────────────────────────────────

def _load_state(path: str):
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
    with open(path, "w") as f:
        json.dump(state, f, indent=2)


# ─────────────────────────────────────────────
#  Funkcje pomocnicze
# ─────────────────────────────────────────────

def _delete_message(chat_id, message_id):
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
    state_file = f"state/telegram_state_{symbol}.json"
    state = _load_state(state_file)
    last_id = state.get("last_production_message_id")

    if last_id:
        for chat_id in TELEGRAM_CHAT_IDS:
            _delete_message(chat_id, last_id)

    new_id = None
    for chat_id in TELEGRAM_CHAT_IDS:
        new_id = _send(chat_id, text)

    state["last_production_message_id"] = new_id
    _save_state(state_file, state)


# ─────────────────────────────────────────────
#  Alert systemowy — wspólny
# ─────────────────────────────────────────────

def send_system_alert(text: str):
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

def send_buy_alert(symbol: str, price: float, sl: float, tp: float, ts: float):
    text = fmt_buy(symbol, price, sl, tp, ts)
    send_production_alert(symbol, text)



def send_sell_alert(
    symbol: str,
    price: float,
    pnl: float | None,
    sl: float | None,
    tp: float | None,
    ts: float | None,
    reason: str | None,
):
    text = fmt_sell(symbol, price, pnl, sl, tp, ts, reason)
    send_production_alert(symbol, text)



# ─────────────────────────────────────────────
#  START STATUS PRO — z polskim podsumowaniem
# ─────────────────────────────────────────────

def _format_start_status_status_line(signal: str | None, meta: dict) -> str:
    buy_possible = bool(meta.get("buy_possible"))
    sell_possible = bool(meta.get("sell_possible"))

    if buy_possible and not sell_possible:
        return "BUY możliwy (warunki spełnione)"
    if sell_possible and not buy_possible:
        return "SELL możliwy (warunki spełnione)"
    if buy_possible and sell_possible:
        return "BUY i SELL możliwe (logika do doprecyzowania)"
    return "Brak sygnału (neutralny stan strategii)"


def _format_start_status_text(symbol: str, interval: str, mode: str, signal: str | None, meta: dict) -> str:
    price = meta.get("price")
    atr = meta.get("atr")
    ema_fast = meta.get("ema_fast")
    ema_slow = meta.get("ema_slow")
    rsi = meta.get("rsi")
    stoch_k = meta.get("stoch_k")
    stoch_d = meta.get("stoch_d")
    macd = meta.get("macd")
    macd_signal = meta.get("macd_signal")

    filters_passed = meta.get("filters_passed")
    filters_total = meta.get("filters_total")
    trend_4h = meta.get("trend_4h")
    momentum = meta.get("momentum")
    rsi_trend = meta.get("rsi_trend")
    big_trend = meta.get("big_trend")

    status_line = _format_start_status_status_line(signal, meta)

    lines = []

    lines.append(f"🔵 START STATUS — {symbol}")
    lines.append(f"Tryb: {mode} | Interwał: {interval}")
    if price is not None:
        lines.append(f"Cena: {price:.4f}")
    else:
        lines.append("Cena: brak danych")

    lines.append("")
    lines.append(status_line)

    if filters_passed is not None and filters_total is not None:
        lines.append(f"Filtry: {filters_passed}/{filters_total} OK")

    lines.append("")
    if trend_4h:
        lines.append(f"Trend 4H: {trend_4h}")
    if momentum:
        lines.append(f"Momentum: {momentum}")
    if rsi is not None:
        lines.append(f"RSI: {rsi:.2f} ({rsi_trend or 'N/A'})")
    if stoch_k is not None and stoch_d is not None:
        lines.append(f"Stoch K/D: {stoch_k:.2f} / {stoch_d:.2f}")
    if macd is not None and macd_signal is not None:
        arrow = "↑" if macd > macd_signal else "↓"
        lines.append(f"MACD: {macd:.6f} vs signal {macd_signal:.6f} ({arrow})")
    if atr is not None:
        lines.append(f"ATR: {float(atr):.4f}")

    if big_trend:
        lines.append("")
        lines.append(f"Big Trend: {big_trend}")

    # ─────────────────────────────────────────────
    #  REKOMENDOWANE SL / TP / TS (jeśli dostępne)
    # ─────────────────────────────────────────────
    rec_sl = meta.get("recommended_sl")
    rec_tp = meta.get("recommended_tp")
    rec_ts = meta.get("recommended_ts")

    if rec_sl is not None or rec_tp is not None or rec_ts is not None:
        lines.append("")
        lines.append("Rekomendowane poziomy (strategia):")
        if rec_sl is not None:
            lines.append(f"SL: {rec_sl:.4f}")
        if rec_tp is not None:
            lines.append(f"TP: {rec_tp:.4f}")
        if rec_ts is not None:
            lines.append(f"TS: {rec_ts:.4f}")

    # ─────────────────────────────────────────────
    #  POLSKIE PODSUMOWANIE — czytelne dla laika
    # ─────────────────────────────────────────────
    summary = meta.get("summary")
    if summary:
        lines.append("")
        lines.append(f"Podsumowanie: {summary}")

    return "\n".join(lines)


def send_start_status_alert(symbol: str, interval: str, mode: str, signal: str | None, meta: dict):
    text = _format_start_status_text(symbol, interval, mode, signal, meta)
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
