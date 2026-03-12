import sqlite3, logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


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
    """Sprawdzanie czy tabela, w której będą umieszczone słowa istnieje"""
    logger.debug("Sprawdzam czy tabela Words istnieje")
    try:
        with dbConnection() as cursor:
            cursor.execute(tableExistQuery,("Words",))
            if cursor.fetchone() is None:
                create_table()
            return True

    except sqlite3.Error as e:
        logger.error(f"Wyszukiwanie czy tabela istnieje nie powiodło się: {e}")
        raise    

def create_table() -> None:
    """Tworzenie tabeli 'Words' """
    try:
        with dbConnection() as cursor:
            cursor.execute(createTableQuery)            
    except sqlite3.Error as e:
        logger.error(f"Błąd tworzenia tabel: {e}")
        raise

def check_if_google_sheet_updated() -> DBResult:
    """Sprawdzanie czy akrusz google sheets był aktualizowany"""
    logger.debug("Sprawdzam liczbę słów w bazie")
    try:
        with dbConnection() as cursor:
            cursor.execute(countQuery)
            return DBResult(success=True, data = cursor.fetchone()[0])
        
    except sqlite3.Error as e:
            logger.error(f"Błąd podczas zliczania słów: {e}")
            return DBResult(success=False, error = str(e))
    
def initialize_database() -> None:
    """Inicjalizacja bazy danych"""
    try:
        if check_if_table_exist():
            logger.info("Stworzono baze danych wraz z tabelą")

    except sqlite3.Error as e:
        pass


if __name__ == "__main__":
    initialize_database()