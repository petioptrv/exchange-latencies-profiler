import logging
from logging.handlers import TimedRotatingFileHandler

from src.config import settings
from src.constants import PROJECT_ROOT


def setup_logging():
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "app.log"

    rotating_handler = TimedRotatingFileHandler(
        filename=log_file,
        when="D",
        interval=1,
        backupCount=2,
        encoding="utf-8"
    )

    logging.basicConfig(
        level=getattr(logging, settings.LOGGING_LEVEL),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            rotating_handler,
            logging.StreamHandler()
        ]
    )
