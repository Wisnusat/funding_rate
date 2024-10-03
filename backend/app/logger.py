import logging
import os
import time
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta

LOG_FILE = "sc.log"
LOG_RETENTION_DAYS = 7  # Set retention period to 7 days (1 week)


def remove_old_logs(log_file, retention_days):
    """
    Remove the log file if it is older than the retention period.
    
    Args:
        log_file (str): The path to the log file.
        retention_days (int): The number of days after which the log file should be deleted.
    """
    if os.path.exists(log_file):
        file_creation_time = os.path.getctime(log_file)
        file_age = datetime.now() - datetime.fromtimestamp(file_creation_time)

        if file_age > timedelta(days=retention_days):
            print(f"Removing old log file: {log_file}")
            os.remove(log_file)


# Remove old logs if they are older than 1 week
remove_old_logs(LOG_FILE, LOG_RETENTION_DAYS)

# Configure logging with a rotating file handler
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=2),  # Rotate after 5MB, keep 2 backups
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

