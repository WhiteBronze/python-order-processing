from pathlib import Path
from src.analyzer import OrderAnalyzer
import pandas as pd
import os
from config import REPORTS_DIR, OUTPUT_FILE
import logging

# Настройка логирования
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    filename='logs/errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def main():
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)

    csv_files = list(Path('data/').glob('*.csv'))
    print(f"Найдено файлов: {len(csv_files)}")

    if not csv_files:
        print("Нет CSV-файлов для обработки")
        logging.warning("Нет CSV-файлов в папке data/")
        return

    results = []

    for file_path in csv_files:
        print(f"\nОбработка: {file_path.name}")

        analyzer = OrderAnalyzer(file_path)
        metrics = analyzer.calculate_metric()

        if metrics:
            results.append(metrics)
            print(f"  Выручка: {metrics['total_revenue']:.2f}")
            print(f"  Средний чек: {metrics['avg_check']:.2f}")
            print(f"  Заказов: {metrics['orders_count']}")
        else:
            print(f"  Ошибка при обработке")

    if results:
        df = pd.DataFrame(results)
        output_path = os.path.join(REPORTS_DIR, OUTPUT_FILE)
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"\nРезультаты сохранены в: {output_path}")
    else:
        print("\nНет результатов для сохранения")


if __name__ == "__main__":
    main()