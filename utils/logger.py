# utils/logger.py — prosty logger z rotacją rozmiaru

import logging
import os
from settings.setting import LOG_MAX_SIZE


def get_logger(name: str) -> logging.Logger:
    """
    Zwraca logger z prostą konfiguracją do konsoli i pliku.
    Plik logu jest rotowany ręcznie po przekroczeniu LOG_MAX_SIZE.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger  # już skonfigurowany

    # Konsola
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(ch)

    # Plik
    log_file = "bot.log"
    if os.path.exists(log_file) and os.path.getsize(log_file) > LOG_MAX_SIZE:
        os.remove(log_file)

    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(fh)

    return logger
