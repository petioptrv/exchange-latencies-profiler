import logging

from sqlmodel import Session

from src.db.db import engine, init_db
from src.logging_config import setup_logging

setup_logging()


def init() -> None:
    with Session(engine) as session:
        init_db(session)


def main() -> None:
    logger = logging.getLogger(__name__)
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
