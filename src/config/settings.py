import logging
from pathlib import Path


def setup_logger(logs_dir: Path) -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(
                logs_dir / "instagram_extractor.log", encoding="utf-8"
            )
        ],
    )
    logger = logging.getLogger(__name__)
    return logger
