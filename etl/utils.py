import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta

def setup_logger():
    os.makedirs('logs', exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    file_handler = RotatingFileHandler(
        'logs/etl.log',
        maxBytes=1_000_000,
        backupCount=5
    )
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s'
    )
    console_handler.setFormatter(console_formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

def get_overlap_start(latest_date, days_overlap=1):
    if latest_date is None:
        return '1900-01-01'
    dt = datetime.strptime(latest_date, '%Y-%m-%d')
    return (dt - timedelta(days=days_overlap)).strftime('%Y-%m-%d')