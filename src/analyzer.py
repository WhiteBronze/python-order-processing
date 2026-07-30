import sys

sys.path.append('..')

import pandas as pd
from config import STATUS_COLUMN, DELIVERED_STATUS, AMOUNT_COLUMN, REPORTS_DIR, LOGS_DIR, OUTPUT_FILE, DATA_DIR
import os
import logging

if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

logging.basicConfig(
    filename=os.path.join(LOGS_DIR, 'errors.log'),
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class OrderAnalyzer:
    def __init__(self):
        self.__data = None
        self.__file_name = None

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

        try:
            delivered = delivered.copy()
            delivered[AMOUNT_COLUMN] = pd.to_numeric(delivered[AMOUNT_COLUMN], errors='raise')
        except Exception as e:
            logging.error(f"Ошибка преобразования '{AMOUNT_COLUMN}' в {self.__file_name}: {str(e)}")
            return None

        try:
            total_revenue = delivered[AMOUNT_COLUMN].sum()
            avg_check = delivered[AMOUNT_COLUMN].mean()
            orders_count = len(delivered)
        except Exception as e:
            logging.error(f"Ошибка при расчёте метрик в {self.__file_name}: {str(e)}")
            return None

        return {
            'file_name': self.__file_name,
            'total_revenue': total_revenue,
            'avg_check': avg_check,
            'orders_count': orders_count
        }

    def process_file(self, file_path):
        self.__data = None
        self.__file_name = os.path.basename(file_path)

        try:
            self.__data = pd.read_csv(file_path)
            self.__data.columns = self.__data.columns.str.lower()
        except Exception as e:
            logging.error(f"Ошибка загрузки {self.__file_name}: {str(e)}")
            return None

        return self.calculate_metric()

    def process_all_files(self, data_dir=DATA_DIR):
        if not os.path.exists(data_dir):
            print(f"Папка {data_dir} не найдена")
            return []

        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]

        if not csv_files:
            print("Нет CSV-файлов для обработки")
            return []

        results = []
        errors = 0

        for file_name in csv_files:
            file_path = os.path.join(data_dir, file_name)
            print(f"Обработка: {file_name}")

            result = self.process_file(file_path)

            if result is not None:
                results.append(result)
                print(f"  Выручка: {result['total_revenue']:.2f}")
                print(f"  Средний чек: {result['avg_check']:.2f}")
                print(f"  Заказов: {result['orders_count']}")
            else:
                errors += 1
                print(f"  Ошибка при обработке")

        print(f"\nОбработано файлов: {len(results)}")
        print(f"Ошибок: {errors}")

        return results

    def save_results(self, results):
        if not results:
            print("Нет данных для сохранения")
            return False

        if not os.path.exists(REPORTS_DIR):
            os.makedirs(REPORTS_DIR)

        df = pd.DataFrame(results)
        output_path = os.path.join(REPORTS_DIR, OUTPUT_FILE)
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"\nРезультаты сохранены в: {output_path}")
        return True