import logging
from typing import Optional


_DEFAULT_LOGGER_NAME = "yaplate-bot"
_LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Returns a configured logger instance.

    - Uses StreamHandler
    - Prevents duplicate handlers
    - Defaults to INFO level
    - Safe to call multiple times
    """
    logger_name = name or _DEFAULT_LOGGER_NAME
    logger = logging.getLogger(logger_name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)

        formatter = logging.Formatter(_LOG_FORMAT)
        handler.setFormatter(formatter)

        logger.addHandler(handler)

        # Prevent double logging if root logger is configured
        logger.propagate = False

    return logger
