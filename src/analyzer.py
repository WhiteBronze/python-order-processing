import sys

sys.path.append('..')

import pandas as pd
from config import STATUS_COLUMN, DELIVERED_STATUS, AMOUNT_COLUMN, LOGS_DIR
import os
import logging

# Настройка логирования
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

logging.basicConfig(
    filename=os.path.join(LOGS_DIR, 'errors.log'),
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class OrderAnalyzer:
    def __init__(self, file_path):
        self.__data = None
        self.__file_name = os.path.basename(file_path)

        try:
            self.__data = pd.read_csv(file_path)
            self.__data.columns = self.__data.columns.str.lower()
        except Exception as e:
            logging.error(f"Ошибка загрузки {self.__file_name}: {str(e)}")
            self.__data = None

    def filter_delivered(self):
        if self.__data is None:
            return None
        if STATUS_COLUMN not in self.__data.columns:
            logging.error(f"Колонка '{STATUS_COLUMN}' не найдена в {self.__file_name}")
            return None
        return self.__data[self.__data[STATUS_COLUMN].str.lower() == DELIVERED_STATUS]

    def calculate_metric(self):
        delivered = self.filter_delivered()
        if delivered is None or delivered.empty:
            return None

        if AMOUNT_COLUMN not in delivered.columns:
            logging.error(f"Колонка '{AMOUNT_COLUMN}' не найдена в {self.__file_name}")
            return None

        return {
            'file_name': self.__file_name,
            'total_revenue': delivered[AMOUNT_COLUMN].sum(),
            'avg_check': delivered[AMOUNT_COLUMN].mean(),
            'orders_count': len(delivered)
        }