import logging
import datetime

def console_log(console_message):
    log_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f'[{log_time}] {console_message}'
    print(log_message)

def set_logging(log_file):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Remove all existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger





