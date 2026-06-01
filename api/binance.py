# api/binance.py — pobieranie świec z Binance (stabilne, czyste)

import requests
import pandas as pd


BASE_URL = "https://api.binance.com/api/v3/klines"


def get_klines(symbol: str, interval: str, limit: int = 200) -> pd.DataFrame:
    """
    Pobiera świece z Binance i zwraca DataFrame.
    Zwraca pusty DataFrame w przypadku błędu.
    """

    params = {
        "symbol": symbol.upper(),
        "interval": interval,
        "limit": limit,
    }

    try:
        r = requests.get(BASE_URL, params=params, timeout=5)
        data = r.json()
    except Exception:
        return pd.DataFrame()

    # Jeśli Binance zwróci błąd
    if not isinstance(data, list):
        return pd.DataFrame()

    # Konwersja do DataFrame
    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])

    # Konwersja typów
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)

    return df
