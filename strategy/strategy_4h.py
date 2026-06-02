# strategy/strategy_4h.py — 4H PRO (EMA TREND + MACD CROSS, ATR + STATUS PRO meta)

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
        return None, {
            "price": None,
            "df": df,
            "buy_possible": False,
            "sell_possible": False,
        }

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

    # RSI (info)
    delta = close.diff()
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    roll_up = pd.Series(gain).rolling(cfg.RSI_PERIOD).mean()
    roll_down = pd.Series(loss).rolling(cfg.RSI_PERIOD).mean()
    rs = roll_up / (roll_down + 1e-9)
    rsi = 100.0 - (100.0 / (1.0 + rs))

    # STOCH (info)
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

    # WARUNKI WEJŚCIA (sensowne, ale nie beton)
    up_trend = last_price > last_ema_slow          # cena ponad EMA slow
    macd_cross_up = prev_macd < prev_signal and last_macd > last_signal  # momentum w górę

    # DEBUG — pełny obraz, ale BUY zależy tylko od UP + MACD
    stoch_from_oversold = prev_k < cfg.STOCH_OS and last_k > prev_k
    rsi_ok = last_rsi > cfg.RSI_MIN

    print(
        f"UP={up_trend} | MACD={macd_cross_up} | STOCH={stoch_from_oversold} | RSI={rsi_ok} | PRICE={last_price}"
    )

    # LOGIKA BUY
    signal: Optional[str] = None
    buy_possible = bool(up_trend and macd_cross_up)
    sell_possible = False  # na razie brak logiki short/SELL w strategii

    if buy_possible:
        signal = "BUY"

    # STATUS PRO — meta do START STATUS i logów
    filters = [
        up_trend,
        macd_cross_up,
    ]
    filters_passed = sum(1 for f in filters if f)
    filters_total = len(filters)

    trend_4h = "UP" if up_trend else "DOWN"
    momentum = "UP" if macd_cross_up or last_macd > last_signal else "DOWN"
    rsi_trend = "UP" if last_rsi >= 50.0 else "DOWN"
    big_trend = trend_4h  # na razie to samo, można później rozbudować

    meta = {
        "price": last_price,
        "df": df,
        "atr": float(atr.iloc[-1]) if hasattr(atr, "iloc") else float(atr),
        "ema_fast": last_ema_fast,
        "ema_slow": last_ema_slow,
        "rsi": last_rsi,
        "stoch_k": last_k,
        "stoch_d": last_d,
        "macd": last_macd,
        "macd_signal": last_signal,
        # STATUS PRO
        "buy_possible": buy_possible,
        "sell_possible": sell_possible,
        "filters_passed": filters_passed,
        "filters_total": filters_total,
        "trend_4h": trend_4h,
        "momentum": momentum,
        "rsi_trend": rsi_trend,
        "big_trend": big_trend,
    }

    return signal, meta
