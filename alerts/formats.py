# alerts/formats.py — formatowanie wiadomości Telegram (czyste, spójne)

def fmt_buy(symbol: str, price: float) -> str:
    """Format alertu BUY."""
    return f"🟢 BUY {symbol}\nCena: {price}"


# def fmt_sell(symbol: str, price: float, pnl: float = None) -> str:
def fmt_sell(symbol: str, price: float, pnl: float | None = None) -> str:

    """Format alertu SELL."""
    if pnl is not None:
        return f"🔴 SELL {symbol}\nCena: {price}\nPnL: {pnl:.2f}"
    return f"🔴 SELL {symbol}\nCena: {price}"


def fmt_system(text: str) -> str:
    """Format alertu systemowego."""
    return f"⚙️ SYSTEM\n{text}"


def fmt_error(symbol: str, error: str) -> str:
    """Format błędu."""
    return f"❗ ERROR {symbol}\n{error}"


def fmt_start(symbol: str, interval: str, mode: str) -> str:
    """Format komunikatu startowego."""
    return f"🚀 START\nSymbol: {symbol}\nInterwał: {interval}\nTryb: {mode}"
