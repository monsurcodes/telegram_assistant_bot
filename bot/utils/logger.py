# bot/utils/logger.py
import logging

def get_logger(name=__name__):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():  # Prevent double logs if re-imported
        stream_handler = logging.StreamHandler()
        file_handler = logging.FileHandler('logs/bot.log', encoding='utf8')
        formatter = logging.Formatter(
            "[%(asctime)s][%(levelname)s][%(name)s] %(message)s"
        )
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
    return logger
