# alerts/formats.py — FINAL PRO VERSION

def _fmt(v):
    """Bezpieczne formatowanie liczb (.2f) — None → N/A"""
    try:
        return f"{float(v):.2f}"
    except:
        return "N/A"


# ─────────────────────────────────────────────
#  LOGIKA STRATEGII — DODANE WERSJE PRO
# ─────────────────────────────────────────────

def compute_strategy_state(filters_ok: int, trend: str) -> str:
    """Zwraca dynamiczny stan strategii."""
    if filters_ok == 2 and trend == "UP":
        return "BUY możliwy"
    if filters_ok == 2 and trend == "DOWN":
        return "SELL możliwy"
    return "brak sygnału"


def compute_summary(trend: str, momentum: str, big_trend: str, filters_ok: int) -> str:
    """Inteligentne podsumowanie sytuacji rynkowej."""
    if filters_ok == 2 and trend == "UP":
        return "warunki sprzyjają BUY"
    if filters_ok == 2 and trend == "DOWN":
        return "warunki sprzyjają SELL"

    if big_trend == "DOWN" and momentum == "UP":
        return "odbicie w trendzie spadkowym — ostrożnie"

    if big_trend == "UP" and momentum == "DOWN":
        return "korekta w trendzie wzrostowym"

    return "neutralnie"


# ─────────────────────────────────────────────
#  ALERTY TRANSAKCYJNE
# ─────────────────────────────────────────────

def fmt_buy(symbol: str, price: float, sl: float, tp: float, ts: float) -> str:
    return (
        f"🟢 BUY — {symbol}\n"
        f"Cena wejścia: {_fmt(price)}\n\n"
        f"SL (Stop Loss): {_fmt(sl)}\n"
        f"TP (Take Profit): {_fmt(tp)}\n"
        f"TS (Trailing Stop): {_fmt(ts)}\n\n"
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

    lines = []
    lines.append(f"🔴 SELL — {symbol}")
    lines.append(f"Cena wyjścia: {_fmt(price)}")

    if pnl is not None:
        lines.append(f"Zysk: {_fmt(pnl)}%")

    if reason:
        lines.append(f"Powód: {reason}")

    if sl is not None or tp is not None or ts is not None:
        lines.append("")
        lines.append("Poziomy strategii:")
        lines.append(f"SL: {_fmt(sl)}")
        lines.append(f"TP: {_fmt(tp)}")
        lines.append(f"TS: {_fmt(ts)}")

    return "\n".join(lines)


def fmt_system(text: str) -> str:
    return f"⚙️ SYSTEM\n{text}"


def fmt_error(symbol: str, error: str) -> str:
    return f"❗ ERROR {symbol}\n{error}"


def fmt_start(symbol: str, interval: str, mode: str) -> str:
    return (
        f"🚀 START\n"
        f"Symbol: {symbol}\n"
        f"Interwał: {interval}\n"
        f"Tryb: {mode}"
    )


# ─────────────────────────────────────────────
#  TREND STATUS PRO — FINALNA WERSJA
# ─────────────────────────────────────────────

def fmt_trend_status(
    symbol: str,
    timeframe: str,
    price: float,
    trend: str,
    momentum: str,
    rsi_val: float,
    rsi_arrow: str,
    macd_line: float,
    macd_signal: float,
    macd_arrow: str,
    stoch_k: float,
    stoch_d: float,
    atr_val: float,
    filters_ok: int,
    strategy_state: str,
    big_trend: str,
    sl: float,
    tp: float,
    ts: float,
    summary: str,
):
    return f"""
📊 TREND STATUS — {symbol} ({timeframe})
Cena: *{_fmt(price)}*

Trend: {trend}
Momentum: {momentum}
RSI: {_fmt(rsi_val)} ({rsi_arrow})
MACD: {_fmt(macd_line)} < {_fmt(macd_signal)} ({macd_arrow})
Stoch: {_fmt(stoch_k)} / {_fmt(stoch_d)}
ATR: {_fmt(atr_val)}

Filtry: {filters_ok}/2 OK
Stan strategii: {strategy_state}

Big Trend: {big_trend}

Rekomendowane poziomy:
SL: {_fmt(sl)}
TP: {_fmt(tp)}
TS: {_fmt(ts)}

Podsumowanie: {summary}
"""
