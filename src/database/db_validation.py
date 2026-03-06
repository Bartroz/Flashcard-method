import sqlite3

from .sql_queries import (
    tableExistQuery,
    createTableQuery,
    countQuery
)
from .models import (
    DBResult,
    dbConnection,
)

def check_if_table_exist() -> bool:
    try:
        with dbConnection() as cursor:
            cursor.execute(tableExistQuery)
            return cursor.fetchone() is not None

    except sqlite3.Error as e:
        print(f"Wyszukiwanie czy tabela istnieje nie powiodło się: {e}")
        raise    

def create_table(missingTable: str) -> None: #tworzenie tabeli
    try:
        with dbConnection() as cursor:
            cursor.execute(createTableQuery)            
    except sqlite3.Error as e:
        print(f"Błąd tworzenia tabel: {e}")
        raise

def check_if_google_sheet_updated() -> DBResult:
    try:
        with dbConnection() as cursor:
            cursor.execute(countQuery)
            return DBResult(success=True, data = cursor.fetchone()[0])
        
    except sqlite3.Error as e:
            print(f"Błąd podczas zliczania słów: {e}")
            return DBResult(success=False, error = str(e))
    
def initialize_database() -> None:
    try:
        if check_if_table_exist():
            print("✓ Tabela istnieje")
        else: 
            # create_table(tableName)
            print(f"Utworzono tabele!")

    except sqlite3.Error as e:
        print(f"Błąd podczas inicjacji bazy danych: {e}")