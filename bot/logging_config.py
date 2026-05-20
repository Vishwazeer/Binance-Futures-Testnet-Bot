import logging
import sys
from pathlib import Path

def setup_logging(log_dir: str = "logs") -> logging.Logger:
    # Ensure logs directory exists relative to current working directory
    Path(log_dir).mkdir(exist_ok=True, parents=True)
    
    logger = logging.getLogger("trading_bot")
    logger.setLevel(logging.DEBUG)

    # Format setup
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S"
    )

    # Prevent adding handlers repeatedly if logging is initialized multiple times
    if not logger.handlers:
        # File handler — DEBUG+
        fh = logging.FileHandler(f"{log_dir}/trading.log", encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)

        # Error file handler — ERROR+
        eh = logging.FileHandler(f"{log_dir}/errors.log", encoding="utf-8")
        eh.setLevel(logging.ERROR)
        eh.setFormatter(fmt)

        # Console handler — INFO+ (keeps terminal output focused)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        ch.setFormatter(fmt)

        logger.addHandler(fh)
        logger.addHandler(eh)
        logger.addHandler(ch)

    return logger
