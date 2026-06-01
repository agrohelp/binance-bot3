# core/position.py — integracja ATR PRO (BUY/SELL + SL/TP/TS)

from typing import Tuple, Optional
from strategy.utils import atr_pro_trailing


def update_position_with_signal(
    symbol: str,
    signal: Optional[str],
    meta: dict,
    position_state: dict,
    cfg,
) -> Tuple[dict, Optional[str]]:
    """
    Główna logika pozycji:
    - BUY → otwarcie pozycji
    - SELL → zamknięcie pozycji
    - ATR PRO → trailing stop
    """

    alert_text = None
    current_position = position_state.get("position")
    price = meta.get("price")

    # ─────────────────────────────────────────────
    # 1. BUY — otwarcie pozycji
    # ─────────────────────────────────────────────
    if signal == "BUY" and current_position is None:
        position_state["position"] = "LONG"
        position_state["entry_price"] = price
        position_state["sl"] = None
        position_state["tp"] = None
        position_state["ts_active"] = False

        alert_text = f"🟢 BUY {symbol} @ {price}"
        return position_state, alert_text

    # ─────────────────────────────────────────────
    # 2. SELL — zamknięcie pozycji
    # ─────────────────────────────────────────────
    if signal == "SELL" and current_position == "LONG":
        entry = position_state.get("entry_price")
        pnl = price - entry if entry is not None else None

        position_state["position"] = None
        position_state["entry_price"] = None
        position_state["sl"] = None
        position_state["tp"] = None
        position_state["ts_active"] = False

        if pnl is not None:
            alert_text = f"🔴 SELL {symbol} @ {price} | PnL: {pnl:.2f}"
        else:
            alert_text = f"🔴 SELL {symbol} @ {price}"

        return position_state, alert_text

    # ─────────────────────────────────────────────
    # 3. ATR PRO — trailing stop
    # ─────────────────────────────────────────────
    if current_position == "LONG":
        position_state, ts_alert = atr_pro_trailing(
            meta["df"],  # przekazujemy pełne świece
            position_state,
            cfg,
        )

        if ts_alert:
            return position_state, ts_alert

        # Sprawdzenie SL (TS)
        sl = position_state.get("sl")
        if sl and price <= sl:
            entry = position_state.get("entry_price")
            pnl = price - entry if entry is not None else None

            position_state["position"] = None
            position_state["entry_price"] = None
            position_state["sl"] = None
            position_state["tp"] = None
            position_state["ts_active"] = False

            if pnl is not None:
                alert_text = f"🔴 SL HIT {symbol} @ {price} | PnL: {pnl:.2f}"
            else:
                alert_text = f"🔴 SL HIT {symbol} @ {price}"

            return position_state, alert_text

    return position_state, None
