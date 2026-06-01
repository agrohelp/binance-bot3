# core/runner.py — pobieranie świec dla symbolu (realne API)

from api.binance import get_klines
import pandas as pd


def fetch_candles_for_symbol(symbol: str, interval: str, limit: int) -> pd.DataFrame:
    """
    Pobiera realne świece z Binance.
    """
    df = get_klines(symbol, interval, limit)

    if df is None or df.empty:
        return pd.DataFrame()

    return df
