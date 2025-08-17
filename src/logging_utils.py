import logging

from src.config import settings
from src.constants import BACKEND_ROOT_PATH


def setup_logging():
    log_dir = BACKEND_ROOT_PATH / "logs"
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "app.log"

    logging.basicConfig(
        level=getattr(logging, settings.LOGGING_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
