import os
import logging


def setup_logging():
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.getLogger(__name__).info(f"Logging initialized with level {log_level}")
