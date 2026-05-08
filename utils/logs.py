"""
utils/logs.py
─────────────
Configures a colourful, consistent logger used by every module.
"""

import logging
import os
from utils.constants import LOG_FORMAT, LOG_DATE_FORMAT

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
    _COLORS = {
        "DEBUG":    Fore.CYAN,
        "INFO":     Fore.GREEN,
        "WARNING":  Fore.YELLOW,
        "ERROR":    Fore.RED,
        "CRITICAL": Fore.MAGENTA,
    }
except ImportError:
    _COLORS = {}


class ColorFormatter(logging.Formatter):
    """Add ANSI colours to log level names when a terminal is attached."""

    def format(self, record: logging.LogRecord) -> str:
        color = _COLORS.get(record.levelname, "")
        if color:
            record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger.  Call this at the top of every module::

        from utils.logs import get_logger
        logger = get_logger(__name__)
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        level_name = os.getenv("LOG_LEVEL", "INFO").upper()
        level = getattr(logging, level_name, logging.INFO)
        logger.setLevel(level)

        handler = logging.StreamHandler()
        handler.setFormatter(ColorFormatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
        logger.addHandler(handler)

    return logger
