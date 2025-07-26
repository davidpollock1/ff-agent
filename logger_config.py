# logging_config.py
import logging
import os

LOG_FILE = "app.log"
LOG_LEVEL = logging.INFO

# Ensure the log file directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True) if os.path.dirname(
    LOG_FILE
) else None

logging.basicConfig(
    level=LOG_LEVEL,
    format="[%(asctime)s] %(levelname)s in %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),  # Optional: also print to console
    ],
)
