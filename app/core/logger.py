import logging
from logging.handlers import RotatingFileHandler
import sys
from app.core.config import settings

class SingletonLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            # Create the logger
            logger = logging.getLogger("app_logger")
            logger.setLevel(logging.DEBUG)

            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

            # File handler (rotating logs)
            file_handler = RotatingFileHandler(
                settings.LOG_FILE or "app.log", maxBytes=10*1024*1024, backupCount=5
            )
            file_handler.setLevel(logging.INFO)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

            cls._instance = logger

        return cls._instance


def get_logger():
    return SingletonLogger()
