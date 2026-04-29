"""Настройка структурированного логирования в формате JSON."""
import logging
import sys
from pythonjsonlogger import jsonlogger


def setup_logging():
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s (%(task_id)s)"
    )
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    # Установим уровень для aiokafka, чтобы не спамил
    logging.getLogger("aiokafka").setLevel(logging.WARNING)