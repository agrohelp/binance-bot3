# bot.py — v2.3 PRO (TREND STATUS FIXED + exit_reason + SL/TP/TS + NO START LOOP)
print("ŁADUJĘ TEN PLIK:", __file__)

import importlib
import sys
import time

from settings.setting import (
    MODE,
    TREND_STATUS_ENABLED,
    TREND_STATUS_TIMEFRAME,
    TREND_STATUS_INTERVAL_MINUTES,
    TREND_STATUS_SYMBOL,
)

from utils.logger import get_logger
from core.runner import fetch_candles_for_symbol
from core.state import load_position_state, save_position_state
from core.position import update_position_with_signal
from strategy.strategy_4h import generate_signal

# ALERTY
from alerts.telegram import (
    send_start_alert,
    send_system_alert,
    send_buy_alert,
    send_sell_alert,
    send_error_alert,
    send_start_status_alert,
    send_trend_status_alert,
)

from alerts.formats import (
    fmt_trend_status,
    compute_strategy_state,
    compute_summary,
)

logger = get_logger(__name__)


def load_symbol_setting(module_name: str):
    try:
        return importlib.import_module(f"settings.{module_name}")
    except ModuleNotFoundError:
        raise RuntimeError(f"Nie znaleziono modułu settings/{module_name}.py")


def main():
    if len(sys.argv) < 2:
        print("Użycie: python bot.py setting_btc")
        sys.exit(1)

    cfg = load_symbol_setting(sys.argv[1])

    symbol = cfg.SYMBOL
    interval = cfg.INTERVAL

    logger.info(f"Start bota dla {symbol} na interwale {interval} (MODE={MODE})")
    send_start_alert(symbol, interval, MODE)

    # START STATUS PRO — wykonuje się tylko raz
    try:
        df_start = fetch_candles_for_symbol(symbol, interval, cfg.CANDLES)
        if df_start is not None and not df_start.empty:
            signal_start, meta_start = generate_signal(df_start, cfg)
            send_start_status_alert(symbol, interval, MODE, signal_start, meta_start)
    except Exception as e:
        logger.exception(f"Błąd START STATUS: {e}")
        send_error_alert(symbol, e)

    # Wczytaj stan pozycji
    position_state = load_position_state(symbol)

    # TREND STATUS timestamp tylko dla symbolu TREND_STATUS_SYMBOL
    if symbol == TREND_STATUS_SYMBOL:
        last_trend_status = position_state.get("last_trend_status", 0)
    else:
        last_trend_status = 0  # zapobiega pętli alertów startowych

    while True:
        try:
            # 1. Pobierz świece
            df = fetch_candles_for_symbol(symbol, interval, cfg.CANDLES)
            if df is None or df.empty:
                logger.warning(f"Brak danych dla {symbol}")
                time.sleep(10)
                continue

            # 2. Sygnał strategii
            signal, meta = generate_signal(df, cfg)

            # 3. Logika pozycji
            position_state, alert = update_position_with_signal(
                symbol=symbol,
                signal=signal,
                meta=meta,
                position_state=position_state,
                cfg=cfg,
            )

            # 4. Zapis stanu
            save_position_state(symbol, position_state)

            # 5. ALERTY PRODUKCYJNE
            if alert:
                parts = alert.split()

                # BUY
                if parts[0] == "BUY" or "BUY" in alert:
                    price = float(parts[1])
                    send_buy_alert(
                        symbol,
                        price,
                        meta["recommended_sl"],
                        meta["recommended_tp"],
                        meta["recommended_ts"],
                    )

                # SELL
                elif "SELL" in alert or "HIT" in alert:
                    price = float(parts[1])
                    exit_reason = position_state.get("exit_reason")
                    send_sell_alert(
                        symbol,
                        price,
                        None,
                        meta.get("recommended_sl"),
                        meta.get("recommended_tp"),
                        meta.get("recommended_ts"),
                        exit_reason,
                    )

            # ─────────────────────────────────────────────
            #  TREND STATUS PRO
            # ─────────────────────────────────────────────
            now = time.time()

            if (
                TREND_STATUS_ENABLED
                and symbol == TREND_STATUS_SYMBOL
                and now - last_trend_status >= TREND_STATUS_INTERVAL_MINUTES * 60
            ):
                try:
                    df_ts = fetch_candles_for_symbol(
                        TREND_STATUS_SYMBOL,
                        TREND_STATUS_TIMEFRAME,
                        cfg.CANDLES,
                    )

                    signal_ts, meta_ts = generate_signal(df_ts, cfg)

                    price = meta_ts.get("price")
                    trend = meta_ts.get("trend_4h")
                    momentum = meta_ts.get("momentum")
                    rsi_val = meta_ts.get("rsi")
                    rsi_arrow = "↑" if meta_ts.get("rsi_trend") == "UP" else "↓"
                    macd_line = meta_ts.get("macd")
                    macd_signal = meta_ts.get("macd_signal")
                    macd_arrow = "↑" if (macd_line and macd_signal and macd_line > macd_signal) else "↓"
                    stoch_k = meta_ts.get("stoch_k")
                    stoch_d = meta_ts.get("stoch_d")
                    atr_val = meta_ts.get("atr")
                    filters_ok = meta_ts.get("filters_passed", 0)

                    # NOWE — pełna logika PRO
                    strategy_state = compute_strategy_state(filters_ok, trend)
                    big_trend = trend  # dopóki nie dodamy 1D
                    sl = meta_ts.get("recommended_sl")
                    tp = meta_ts.get("recommended_tp")
                    ts = meta_ts.get("recommended_ts")
                    summary = compute_summary(trend, momentum, big_trend, filters_ok)

                    text = fmt_trend_status(
                        TREND_STATUS_SYMBOL,
                        TREND_STATUS_TIMEFRAME,
                        price,
                        trend,
                        momentum,
                        rsi_val,
                        rsi_arrow,
                        macd_line,
                        macd_signal,
                        macd_arrow,
                        stoch_k,
                        stoch_d,
                        atr_val,
                        filters_ok,
                        strategy_state,
                        big_trend,
                        sl,
                        tp,
                        ts,
                        summary,
                    )

                    send_trend_status_alert(text)

                except Exception as e:
                    logger.error(f"TREND STATUS error: {e}")

                # Zapisz timestamp tylko dla symbolu TREND_STATUS_SYMBOL
                last_trend_status = now
                position_state["last_trend_status"] = last_trend_status
                save_position_state(symbol, position_state)

        except Exception as e:
            logger.exception(f"Błąd głównej pętli: {e}")
            send_error_alert(symbol, e)

        time.sleep(10)


if __name__ == "__main__":
    main()
