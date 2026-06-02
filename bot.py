# bot.py — v0.1.4 PRO (single-symbol, stabilny, z pełnymi START STATUS alertami)

import importlib
import sys
import time

from settings.setting import MODE
from utils.logger import get_logger
from core.runner import fetch_candles_for_symbol
from core.state import load_position_state, save_position_state
from core.position import update_position_with_signal
from strategy.strategy_4h import generate_signal

# ALERTY v0.1.4
from alerts.telegram import (
    send_start_alert,
    send_system_alert,
    send_buy_alert,
    send_sell_alert,
    send_error_alert,
    send_start_status_alert,
)

logger = get_logger(__name__)


def load_symbol_setting(module_name: str):
    """
    Dynamicznie ładuje moduł z katalogu settings/ (np. setting_btc).
    """
    try:
        return importlib.import_module(f"settings.{module_name}")
    except ModuleNotFoundError:
        raise RuntimeError(f"Nie znaleziono modułu settings/{module_name}.py")


def main():
    """
    Główna pętla bota:
    - ładuje config symbolu
    - pobiera świece
    - wywołuje czystą strategię
    - aktualizuje stan pozycji
    - wysyła alerty
    """
    if len(sys.argv) < 2:
        print("Użycie: python bot.py setting_btc")
        sys.exit(1)

    setting_module_name = sys.argv[1]
    cfg = load_symbol_setting(setting_module_name)

    symbol = cfg.SYMBOL
    interval = cfg.INTERVAL

    # ALERT START (systemowy)
    logger.info(f"Start bota dla {symbol} na interwale {interval} (MODE={MODE})")
    send_start_alert(symbol, interval, MODE)

    # START STATUS (produkcyjny, STATUS PRO na podstawie aktualnego stanu strategii)
    try:
        df_start = fetch_candles_for_symbol(symbol, interval, cfg.CANDLES)

        if df_start is None or df_start.empty:
            logger.warning(f"Brak danych dla {symbol} przy starcie — pomijam START STATUS.")
        else:
            signal_start, meta_start = generate_signal(df_start, cfg)
            # produkcyjny status BUY/SELL/NEUTRAL na wejściu
            send_start_status_alert(symbol, interval, MODE, signal_start, meta_start)
    except Exception as e:
        logger.exception(f"Błąd przy generowaniu START STATUS dla {symbol}: {e}")
        send_error_alert(symbol, e)

    # Stan pozycji dla danego symbolu
    position_state = load_position_state(symbol)

    while True:
        try:
            # 1. Pobierz świece
            df = fetch_candles_for_symbol(symbol, interval, cfg.CANDLES)

            if df is None or df.empty:
                logger.warning(f"Brak danych dla {symbol}, pomijam iterację.")
                time.sleep(10)
                continue

            # 2. Wygeneruj sygnał strategii
            signal, meta = generate_signal(df, cfg)

            # 3. Zaktualizuj stan pozycji
            position_state, alert = update_position_with_signal(
                symbol=symbol,
                signal=signal,
                meta=meta,
                position_state=position_state,
                cfg=cfg,
            )

            # 4. Zapisz stan pozycji
            save_position_state(symbol, position_state)

            # 5. ALERTY PRODUKCYJNE (BUY / SELL)
            if alert:
                # alert = np. "BUY 123.45" albo "SELL 125.00 PnL: 1.55"
                parts = alert.split()

                if parts[0] == "BUY":
                    price = float(parts[1])
                    send_buy_alert(symbol, price)

                elif parts[0] == "SELL":
                    price = float(parts[1])
                    pnl = float(parts[3]) if len(parts) > 3 else None
                    send_sell_alert(symbol, price, pnl)

        except Exception as e:
            # ALERT ERROR
            logger.exception(f"Błąd głównej pętli dla {symbol}: {e}")
            send_error_alert(symbol, e)

        time.sleep(10)


if __name__ == "__main__":
    main()
