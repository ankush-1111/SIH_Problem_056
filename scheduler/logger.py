import logging
import sys

def setup_logger():
    logger = logging.getLogger("scheduler")
    logger.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger

logger = setup_logger()