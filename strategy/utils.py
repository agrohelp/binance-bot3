# strategy/utils.py — ATR PRO ENGINE (hybryda: dynamiczny + klasyczny fallback)

from typing import Optional, Tuple
import pandas as pd
from .indicators import atr_core


# ─────────────────────────────────────────────
# 1. Klasyfikacja zmienności
# ─────────────────────────────────────────────

def classify_volatility(atr: float, price: float) -> str:
    """
    Klasyfikacja zmienności na podstawie ATR/price.
    """
    if atr is None or price is None:
        return "unknown"

    ratio = atr / price

    if ratio < 0.005:
        return "low"
    if ratio < 0.015:
        return "medium"
    return "high"


# ─────────────────────────────────────────────
# 2. Dynamic ATR Factor
# ─────────────────────────────────────────────

def dynamic_atr_factor(vol_class: str) -> float:
    """
    Dynamiczny mnożnik ATR zależny od zmienności.
    """
    if vol_class == "low":
        return 3.0
    if vol_class == "medium":
        return 2.0
    if vol_class == "high":
        return 1.2
    return 2.0  # fallback


# ─────────────────────────────────────────────
# 3. ATR PRO Trailing Engine
# ─────────────────────────────────────────────

def atr_pro_trailing(
    df: pd.DataFrame,
    position_state: dict,
    cfg,
) -> Tuple[dict, Optional[str]]:
    """
    ATR PRO:
    - aktywacja TS
    - podciąganie TS
    - reset TS
    - dynamiczny ATR factor
    """

    alert_text = None

    if position_state.get("position") != "LONG":
        return position_state, None

    # Ostatnia cena
    last_price = float(df["close"].iloc[-1])

    # ATR
    atr = atr_core(df, cfg.ATR_PERIOD)
    if atr is None:
        return position_state, None

    # Klasa zmienności
    vol_class = classify_volatility(atr, last_price)

    # Dynamiczny mnożnik ATR
    factor = dynamic_atr_factor(vol_class)

    # Nowy trailing stop
    new_ts = last_price - atr * factor

    # Jeśli TS nieaktywny → aktywuj
    if not position_state.get("ts_active"):
        position_state["ts_active"] = True
        position_state["sl"] = new_ts
        alert_text = f"🔵 TS aktywowany @ {new_ts:.4f}"
        return position_state, alert_text

    # Jeśli TS aktywny → podciągaj
    old_ts = position_state.get("sl")

    if new_ts > old_ts:
        position_state["sl"] = new_ts
        alert_text = f"🔵 TS podciągnięty @ {new_ts:.4f}"

    return position_state, alert_text
