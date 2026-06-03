# alerts/formats.py — formatowanie wiadomości Telegram (czyste, spójne)

def fmt_buy(symbol: str, price: float, sl: float, tp: float, ts: float) -> str:
    """Format alertu BUY — z rekomendowanym SL/TP/TS."""
    return (
        f"🟢 BUY — {symbol}\n"
        f"Cena wejścia: {price:.2f}\n\n"
        f"SL (Stop Loss): {sl:.2f}\n"
        f"TP (Take Profit): {tp:.2f}\n"
        f"TS (Trailing Stop): {ts:.2f}\n\n"
        f"Powód: spełnione warunki strategii"
    )


def fmt_sell(
    symbol: str,
    price: float,
    pnl: float | None = None,
    sl: float | None = None,
    tp: float | None = None,
    ts: float | None = None,
    reason: str | None = None,
) -> str:
    """Format alertu SELL — z pełnym kontekstem SL/TP/TS."""

    lines = []
    lines.append(f"🔴 SELL — {symbol}")
    lines.append(f"Cena wyjścia: {price:.2f}")

    if pnl is not None:
        lines.append(f"Zysk: {pnl:.2f}%")

    # Powód zamknięcia pozycji
    if reason:
        lines.append(f"Powód: {reason}")

    # Rekomendowane poziomy (jeśli dostępne)
    if sl is not None or tp is not None or ts is not None:
        lines.append("")
        lines.append("Poziomy strategii:")
        if sl is not None:
            lines.append(f"SL: {sl:.2f}")
        if tp is not None:
            lines.append(f"TP: {tp:.2f}")
        if ts is not None:
            lines.append(f"TS: {ts:.2f}")

    return "\n".join(lines)



def fmt_system(text: str) -> str:
    """Format alertu systemowego."""
    return f"⚙️ SYSTEM\n{text}"


def fmt_error(symbol: str, error: str) -> str:
    """Format błędu."""
    return f"❗ ERROR {symbol}\n{error}"


def fmt_start(symbol: str, interval: str, mode: str) -> str:
    """Format komunikatu startowego."""
    return (
        f"🚀 START\n"
        f"Symbol: {symbol}\n"
        f"Interwał: {interval}\n"
        f"Tryb: {mode}"
    )
