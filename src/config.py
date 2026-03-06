from pathlib import Path

# Katalog główny projektu (gdzie jest config.py)
BASE_DIR = Path(__file__).resolve().parent

# Katalog data/
DATA_DIR = BASE_DIR / "data"

# Ścieżka do bazy danych
DB_PATH = DATA_DIR / "GermanLearning.db"

# Ścieżka do credentials
CREDENTIALS_PATH = DATA_DIR / "credentials.json"

for i in BASE_DIR.iterdir():
    print(i)