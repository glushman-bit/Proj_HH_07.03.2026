from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

path_file = DATA_DIR / "companies.txt"


def read_companies_from_file(path_file):
    """Чтение списка компаний из файла."""
    with open(path_file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]
