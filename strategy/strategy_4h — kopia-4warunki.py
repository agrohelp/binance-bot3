# strategy/strategy_4h.py — 4H PRO (EMA + MACD + RSI + STOCH + ATR meta)

from typing import Tuple, Optional
import pandas as pd
import numpy as np

from strategy.indicators import atr_core


def _ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def _macd(series: pd.Series, fast: int, slow: int, signal: int):
    ema_fast = _ema(series, fast)
    ema_slow = _ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


def _stoch(df: pd.DataFrame, k_period: int = 14, d_period: int = 3):
    low_min = df["low"].rolling(k_period).min()
    high_max = df["high"].rolling(k_period).max()
    k = (df["close"] - low_min) / (high_max - low_min) * 100
    d = k.rolling(d_period).mean()
    return k, d


def generate_signal(df: pd.DataFrame, cfg) -> Tuple[Optional[str], dict]:

    # Guard
    if df is None or df.empty or len(df) < max(50, cfg.ATR_PERIOD + 5):
        return None, {"price": None, "df": df}

    close = df["close"]

    # EMA
    ema_fast = _ema(close, cfg.EMA_FAST)
    ema_slow = _ema(close, cfg.EMA_SLOW)

    # MACD
    macd_line, signal_line, hist = _macd(
        close,
        cfg.MACD_FAST,
        cfg.MACD_SLOW,
        cfg.MACD_SIGNAL,
    )

    # RSI
    delta = close.diff()
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    roll_up = pd.Series(gain).rolling(cfg.RSI_PERIOD).mean()
    roll_down = pd.Series(loss).rolling(cfg.RSI_PERIOD).mean()
    rs = roll_up / (roll_down + 1e-9)
    rsi = 100.0 - (100.0 / (1.0 + rs))

    # STOCH
    k, d = _stoch(df, cfg.STOCH_K, cfg.STOCH_D)

    # ATR
    atr = atr_core(df, cfg.ATR_PERIOD)
    last_price = float(close.iloc[-1])

    # Ostatnia świeca
    last_ema_fast = float(ema_fast.iloc[-1])
    last_ema_slow = float(ema_slow.iloc[-1])
    last_macd = float(macd_line.iloc[-1])
    prev_macd = float(macd_line.iloc[-2])
    last_signal = float(signal_line.iloc[-1])
    prev_signal = float(signal_line.iloc[-2])
    last_rsi = float(rsi.iloc[-1])
    last_k = float(k.iloc[-1])
    prev_k = float(k.iloc[-2])
    last_d = float(d.iloc[-1])

    # Warunki
    up_trend = last_price > last_ema_slow
    macd_cross_up = prev_macd < prev_signal and last_macd > last_signal
    stoch_from_oversold = prev_k < cfg.STOCH_OS and last_k > prev_k
    rsi_ok = last_rsi > cfg.RSI_MIN

    # DEBUG
    print(
        f"UP={up_trend} | MACD={macd_cross_up} | STOCH={stoch_from_oversold} | RSI={rsi_ok} | PRICE={last_price}"
    )

    # LOGIKA PRODUKCYJNA (bez wymuszenia BUY)
    signal = None
    if up_trend and macd_cross_up and stoch_from_oversold and rsi_ok:
        signal = "BUY"

    # META
    meta = {
        "price": last_price,
        "df": df,
        "atr": atr,
        "ema_fast": last_ema_fast,
        "ema_slow": last_ema_slow,
        "rsi": last_rsi,
        "stoch_k": last_k,
        "stoch_d": last_d,
        "macd": last_macd,
        "macd_signal": last_signal,
    }

    return signal, meta
