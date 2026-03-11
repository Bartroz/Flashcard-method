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
            cursor.execute(tableExistQuery,("Words",))
            
            if cursor.fetchone() is None:
                create_table()
            
            return True

    except sqlite3.Error as e:
        print(f"Wyszukiwanie czy tabela istnieje nie powiodło się: {e}")
        raise    

def create_table() -> None: #tworzenie tabeli
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
            create_table("Words")
            print(f"Utworzono tabele!")

    except sqlite3.Error as e:
        print(f"Błąd podczas inicjacji bazy danych: {e}")


if __name__ == "__main__":
    initialize_database()