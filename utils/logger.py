import logging
from datetime import datetime
import os

# Color codes for ANSI terminal
COLORS = {
    'DEBUG': '\033[36m',     # Cyan
    'INFO': '\033[33m',      # Yellow
    'WARNING': '\033[35m',   # Magenta
    'ERROR': '\033[31m',     # Red
    'CRITICAL': '\033[41m',  # Red Background
    'RESET': '\033[0m'
}

class ColorFormatter(logging.Formatter):
    def format(self, record):
        level_color = COLORS.get(record.levelname, COLORS['RESET'])
        reset = COLORS['RESET']
        record.levelname = f"{level_color}{record.levelname}{reset}"
        return super().format(record)

def setup_logger():
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger("hansenbot")
    logger.setLevel(logging.DEBUG)

    # File Handler (plain, no colors)
    file_handler = logging.FileHandler(f"logs/{datetime.now().strftime('%Y-%m-%d')}.log", encoding="utf-8")
    file_format = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
    file_handler.setFormatter(file_format)

    # Console Handler (colored)
    console_handler = logging.StreamHandler()
    console_format = ColorFormatter('[%(levelname)s] %(message)s')
    console_handler.setFormatter(console_format)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
