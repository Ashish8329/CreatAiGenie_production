import logging
import os

# Set up the logger for the application
def setup_logger(log_level=logging.INFO):
    """
    Setup the logger for the application with the given log level.
    The log messages will be written to both the console and a file.
    """
    # Create the logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Define the log file path
    log_file_path = os.path.join(log_dir, "application.log")

    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)

    # Create a file handler to log messages to a file
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(log_level)

    # Create a console handler to log messages to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # Define log message format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)

    # Set the formatter for both handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Instantiate the logger for use throughout the app
logger = setup_logger()

