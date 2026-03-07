import logging
import sys

from pythonjsonlogger.json import JsonFormatter


def setup_logger(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("emoagent")
    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stdout)
    formatter = JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger
