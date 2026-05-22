import logging
import os
import sys
import traceback
from logging.handlers import RotatingFileHandler
from src.utils import get_resource_path  # type: ignore[import]

def setup_logger():
    """Sets up a robust rotating file logger and console output."""
    log_dir = get_resource_path("logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "divya_drishti.log")

    logger = logging.getLogger("DivyaDrishti")
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers if setup is called multiple times
    if logger.handlers:
        return logger

    # Formatting
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | [%(filename)s:%(lineno)d] | %(message)s'
    )

    # File Handler (Rotating, max 5MB per file, keep 3 backups)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Global App Logger
app_logger = setup_logger()

# Global Exception Hook to prevent silent crashes
def exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
        
    app_logger.critical("Uncaught Exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = exception_handler
