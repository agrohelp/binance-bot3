SYMBOL = "ETHUSDC"      # Para handlowa (np. BTCUSDT, ETHUSDC)
INTERVAL = "4h"         # Interwał świec używany przez strategię
CANDLES = 300           # Ilość świec do pobrania (wystarcza dla EMA/MACD/ATR)

ATR_PERIOD = 14         # Okres ATR – filtr zmienności i sanity check
EMA_FAST = 21           # Szybka EMA – momentum
EMA_SLOW = 55           # Wolna EMA – trend główny

MACD_FAST = 12          # MACD – szybka średnia
MACD_SLOW = 26          # MACD – wolna średnia
MACD_SIGNAL = 9         # MACD – linia sygnału

RSI_PERIOD = 14         # RSI – standardowy okres
RSI_MIN = 48            # Minimalny RSI dla BUY (looser entry)

STOCH_K = 14            # Stochastic – linia K
STOCH_D = 3             # Stochastic – linia D
STOCH_OS = 20           # Poziom wyprzedania (oscylator)


