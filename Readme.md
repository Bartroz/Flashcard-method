# Flashcard Method — Nauka słówek języka niemieckiego

Aplikacja konsolowa do nauki słówek metodą fiszek (Leitner Box System).
Słownictwo pobierane jest z Google Sheets i przechowywane lokalnie w SQLite.

## Funkcje

- Nauka nowych słów
- Kontynuacja nauki słów w trakcie
- Powtarzanie trudnych słów (skuteczność < 60%)
- Automatyczna synchronizacja z Google Sheets
- Śledzenie postępów (liczba prób, skuteczność, komora Leitnera)

## Wymagania

- Python 3.10+
- Konto Google z dostępem do Google Sheets API

## Instalacja

1. Sklonuj repozytorium
   git clone https://github.com/Bartroz/Flashcard-method.git
   cd Flashcard-method

2. Zainstaluj zależności
   pip install -r requirements.txt

3. Skonfiguruj zmienne środowiskowe
   cp .env.example .env
   # Uzupełnij wartości w pliku .env

4. Uruchom aplikację
   python -m src.study

## Konfiguracja Google Sheets

1. Utwórz projekt w Google Cloud Console
2. Włącz Google Sheets API
3. Pobierz plik credentials.json i umieść go w katalogu projektu
4. Uzupełnij SHEET_ID w pliku .env (ID arkusza z URL)

### Format arkusza

| Kolumna A | Kolumna B  | Kolumna C (opcjonalna) | Kolumna D (opcjonalna) |
|-----------|------------|------------------------|------------------------|
| Słowo     | Znaczenie1 | Znaczenie2             | Znaczenie3             |

## Struktura projektu

src/
├── database/
│   ├── db_process.py      # Operacje CRUD na bazie danych
│   ├── db_validation.py   # Inicjalizacja i walidacja bazy
│   ├── models.py          # Modele danych i połączenie z DB
│   └── sql_queries.py     # Zapytania SQL
├── sheets/
│   └── google_sheets_connection.py  # Integracja z Google Sheets API
└── study.py               # Główna logika aplikacji

## Technologie

- SQLite — lokalna baza danych
- gspread — integracja z Google Sheets
- Leitner Box System — algorytm nauki fiszek