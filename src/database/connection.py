import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional, Union

@dataclass
class DBResult():
    success: bool
    data: Optional[Union[list,int]] = None
    error: Optional[str] = None

    @property
    def has_data(self) -> bool:
        if self.data is None:
            return False
        if isinstance(self.data, int):
            return self.data > 0
        if isinstance(self.data, list):
            return len(self.data) > 0

@contextmanager
def dbConnection():
    connection = sqlite3.connect("GermanLearning.db")
    cursor = connection.cursor()
    try:
        yield cursor
        connection.commit()
    except sqlite3.Error as e:
        print(f"Błąd bazy danych: {e}")
        connection.rollback()
        raise
    finally:
        connection.close()