"""
Logging — category 18 from the chat: "Your scraper should tell you
what happened." This will save you during your demo when a judge
asks "what just happened there?"
"""

import logging
import sys

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:  # avoid duplicate handlers if called more than once
        return logger

    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # also write to a file so you have a record after the run finishes
    file_handler = logging.FileHandler("scraper.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
