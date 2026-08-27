import logging
from pathlib import Path


def setup_logging(
    level: str = "INFO",
    log_file: str = "logs/pet_vision.log",
) -> logging.Logger:

    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("pet_vision")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(
        log_file,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger