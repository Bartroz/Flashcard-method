from pathlib import Path
from dotenv import load_dotenv
import os

# src/
BASE_DIR = Path(__file__).resolve().parent

# German/  (root projektu)
PROJECT_ROOT = BASE_DIR.parent

# Załaduj zmienne z pliku .env znajdującego się w root projektu
load_dotenv(PROJECT_ROOT / ".env")

# src/data/
DATA_DIR = BASE_DIR / "data"

# Ścieżka do bazy danych
DB_PATH = DATA_DIR / "GermanLearning.db"

# Ścieżka do credentials
CREDENTIALS_PATH = DATA_DIR / "credentials.json"

#Ścieżka do pliku textowego
INFO_PATH = DATA_DIR / "sheetsInfo.json"

# ID arkusza Google Sheets (pobierane z .env)
SHEET_ID = os.getenv("SHEET_ID")

if not SHEET_ID:
    raise EnvironmentError("Brak zmiennej SHEET_ID w pliku .env")
