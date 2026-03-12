import sqlite3, logging
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional, Union
from src.config import DB_PATH

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

@dataclass
class DBResult():
    success: bool
    data: Optional[Union[list,int]] = None
    error: Optional[str] = None

    @property
    def has_data(self) -> bool:
        if self.data is None:
            logger.info("Brak słów w bazie danych")
            return False
        if isinstance(self.data, int):
            return self.data > 0
        if isinstance(self.data, list):
            return len(self.data) > 0

@contextmanager
def dbConnection():
    logger.debug("Inicjalizacja połączenia z bazą danych")
    connection = sqlite3.connect(str(DB_PATH))
    cursor = connection.cursor()
    try:
        yield cursor
        connection.commit()
    except sqlite3.Error as e:
        logger.critical(f"Błąd bazy danych: {e}")
        connection.rollback()
        raise
    finally:
        connection.close()