# settings/setting.py — globalne ustawienia projektu binance-bot3

import os
from dotenv import load_dotenv

# Wczytaj zmienne środowiskowe z .env
load_dotenv()

# Token bota Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Lista odbiorców alertów produkcyjnych
TELEGRAM_CHAT_IDS = [
    chat_id.strip()
    for chat_id in os.getenv("TELEGRAM_CHAT_IDS", "").split(",")
    if chat_id.strip()
]

# alert TREND-STATUS
TREND_STATUS_ENABLED = True
TREND_STATUS_TIMEFRAME = "4h"          # analizujemy trend na świecach 4H
TREND_STATUS_INTERVAL_MINUTES = 60     # wysyłamy alert co 1 godzinę
TREND_STATUS_SYMBOL = "XRPUSDC"           # główny symbol z settings

# Admin — odbiorca alertów systemowych
TELEGRAM_ADMIN_ID = os.getenv("TELEGRAM_ADMIN_ID")

# Tryb pracy (production / dev)
MODE = os.getenv("MODE", "production")

# Limit rozmiaru logu (100 KB)
LOG_MAX_SIZE = 100_000
