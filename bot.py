# bot.py — binance-bot3, projekt B (multi-symbol, czysta strategia)

import importlib
import sys
import time
from typing import Optional

from settings.setting import MODE
from utils.logger import get_logger
from core.runner import fetch_candles_for_symbol
from core.state import load_position_state, save_position_state
from core.position import update_position_with_signal
from alerts.telegram import send_system_alert, send_production_alert
from strategy.strategy_4h import generate_signal



logger = get_logger(__name__)


def load_symbol_setting(module_name: str):
    """
    Dynamicznie ładuje moduł z katalogu settings/ (np. setting_btc).
    Dzięki temu jeden bot.py obsługuje wiele symboli.
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

    logger.info(f"Start bota dla {symbol} na interwale {interval} (MODE={MODE})")
    send_system_alert(f"Bot start: {symbol} ({interval}), MODE={MODE}")

    # Stan pozycji dla danego symbolu
    position_state = load_position_state(symbol)

    while True:
        try:
            # 1. Pobierz świece dla symbolu
            df = fetch_candles_for_symbol(symbol, interval, cfg.CANDLES)

            if df is None or df.empty:
                logger.warning(f"Brak danych dla {symbol}, pomijam iterację.")
                time.sleep(10)
                continue

            # 2. Wygeneruj sygnał strategii (czysta funkcja)
            signal, meta = generate_signal(df, cfg)

            # 3. Zaktualizuj stan pozycji na podstawie sygnału
            position_state, alert_text = update_position_with_signal(
                symbol=symbol,
                signal=signal,
                meta=meta,
                position_state=position_state,
                cfg=cfg,
            )

            # 4. Zapisz stan pozycji
            save_position_state(symbol, position_state)

            # 5. Wyślij alert produkcyjny (jeśli jest co wysłać)
            if alert_text:
                send_production_alert(alert_text)

        except Exception as e:
            # Globalny bezpiecznik — log + alert systemowy
            logger.exception(f"Błąd głównej pętli dla {symbol}: {e}")
            send_system_alert(f"ERROR {symbol}: {e}")

        # Prosty sleep — w przyszłości możesz to powiązać z czasem świec
        time.sleep(10)


if __name__ == "__main__":
    main()
