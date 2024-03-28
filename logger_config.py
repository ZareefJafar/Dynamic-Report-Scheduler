import logging
from datetime import datetime
from pathlib import Path

class DailyRotatingFileHandler(logging.FileHandler):
    def __init__(self, log_directory):
        self.log_directory = log_directory
        current_date = datetime.now().strftime("%Y-%m-%d")
        log_file_path = log_directory / f"reporting_activity_{current_date}.log"
        super().__init__(log_file_path, mode='a')
        self.current_log_file = log_file_path

    def emit(self, record):
        current_date = datetime.now().strftime("%Y-%m-%d")
        log_file_path = self.log_directory / f"reporting_activity_{current_date}.log"
        if log_file_path != self.current_log_file:
            self.current_log_file = log_file_path
            self.stream.close()
            self.stream = open(log_file_path, self.mode)
        super().emit(record)

def setup_logger():
    # Get the parent directory of the current working directory
    parent_directory = Path.cwd().parent

    # Define the directory where you want to store the log file
    log_directory = parent_directory / "report_activity_logs"

    # Create the log directory if it doesn't exist
    log_directory.mkdir(parents=True, exist_ok=True)

    # Create a custom logger if it doesn't already exist
    logger = logging.getLogger("report_logger")
    if not logger.handlers:
        # Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)
        logger.setLevel(logging.DEBUG)

        # Add the custom daily rotating file handler
        handler = DailyRotatingFileHandler(log_directory)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Log the creation of the log file
        logger.info(f"The log file {handler.current_log_file} created for today.")

    return logger
