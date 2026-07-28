from src.analyzer import OrderAnalyzer
from config import DATA_DIR


def main():
    analyzer = OrderAnalyzer("")

    results = analyzer.process_all_files(DATA_DIR)

    if results:
        analyzer.save_results(results)
        print(f"\nОбработано файлов: {len(results)}")
    else:
        print("\nНет результатов для сохранения")


if __name__ == "__main__":
    main()