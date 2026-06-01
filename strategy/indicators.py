# strategy/indicators.py — ATR CORE (stabilny, odporny na NaN)

import pandas as pd
import numpy as np


def atr_core(df: pd.DataFrame, period: int = 14) -> float:
    """
    Stabilny ATR:
    - odporny na NaN
    - działa nawet przy brakach danych
    - zwraca float lub None
    """

    if df is None or df.empty:
        return None

    if len(df) < period + 1:
        return None

    high = df["high"]
    low = df["low"]
    close = df["close"]

    # True Range
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(period).mean().iloc[-1]

    if np.isnan(atr):
        return None

    return float(atr)
