# strategy/strategy.py — minimalna strategia (dummy), żeby bot działał

from typing import Tuple, Optional
import pandas as pd


def generate_signal(df: pd.DataFrame, cfg) -> Tuple[Optional[str], dict]:
    """
    Minimalna strategia:
    - jeśli brak danych → brak sygnału
    - jeśli close > open → BUY
    - jeśli close < open → SELL
    - jeśli równe → brak sygnału

    Zwraca:
      signal: "BUY", "SELL" lub None
      meta: {"price": float}
    """

    if df is None or df.empty:
        return None, {"price": None}

    # Bierzemy ostatnią świecę
    last = df.iloc[-1]

    try:
        open_price = float(last["open"])
        close_price = float(last["close"])
    except Exception:
        return None, {"price": None}

    # Dummy logika
    if close_price > open_price:
        return "BUY", {"price": close_price}

    if close_price < open_price:
        return "SELL", {"price": close_price}

    return None, {"price": close_price}
