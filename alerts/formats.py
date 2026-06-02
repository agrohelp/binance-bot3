# alerts/formats.py — formatowanie wiadomości Telegram (czyste, spójne)

def fmt_buy(symbol: str, price: float) -> str:
    """Format alertu BUY — nagłówek po angielsku, opisy po polsku."""
    return (
        f"🟢 BUY — {symbol}\n"
        f"Cena wejścia: {price:.2f}\n"
        f"Powód: spełnione warunki strategii"
    )


def fmt_sell(symbol: str, price: float, pnl: float | None = None) -> str:
    """Format alertu SELL — nagłówek po angielsku, opisy po polsku."""
    if pnl is not None:
        return (
            f"🔴 SELL — {symbol}\n"
            f"Cena wyjścia: {price:.2f}\n"
            f"Zysk: {pnl:.2f}%\n"
            f"Powód: zamknięcie pozycji zgodnie ze strategią"
        )
    return (
        f"🔴 SELL — {symbol}\n"
        f"Cena wyjścia: {price:.2f}\n"
        f"Powód: zamknięcie pozycji zgodnie ze strategią"
    )


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
