import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional, Union

tableName:str = "Words"
dbName:str = "GermanLearning.db"

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
    connection = sqlite3.connect(dbName)
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

def check_if_table_exist() -> bool: #sprawdzanie czy DB istnieją - sprawdzane przy uruchomieniu

    try:
        with dbConnection() as cursor:
            sqlquery = """
            SELECT name 
            FROM sqlite_master
            WHERE type = 'table'
            AND name = ?
            """
            cursor.execute(sqlquery,(tableName,))
            return cursor.fetchone() is None

    except sqlite3.Error as e:
        print(f"Wyszukiwanie czy tabela istnieje nie powiodło się: {e}")
        raise
            
def create_table(missingTable: str) -> None: #tworzenie tabeli

    sqlQuery = """
    CREATE Table IF NOT EXISTS Words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT NOT NULL UNIQUE,
        meaning1 TEXT NOT NULL,
        meaning2 TEXT,
        meaning3 TEXT,
        box INTEGER DEFAULT 0,
        total_attempts INTEGER DEFAULT 0,
        total_correct INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_reviewed_at TIMESTAMP
    ); 
    """

    try:
        with dbConnection() as cursor:
            cursor.execute(sqlQuery)            
    except sqlite3.Error as e:
        print(f"Błąd tworzenia tabel: {e}")
        raise
                
def check_if_google_sheet_updated() -> DBResult:
    try:
        with dbConnection() as cursor:

            sqlQuery = """
            SELECT COUNT(*) FROM Words
            """
            cursor.execute(sqlQuery)

            return DBResult(success=True, data = cursor.fetchone()[0])
        
    except sqlite3.Error as e:
            print(f"Błąd podczas zliczania słów: {e}")
            return DBResult(success=False, error = str(e))

def add_word_to_main_db(listOfWords:list[str]) -> bool:

    sqlQuery = """
    INSERT OR IGNORE INTO Words (word, meaning1, meaning2, meaning3)
    VALUES (?,?,?,?)
    """
    try:
        with dbConnection() as cursor:
            
            normalizedWords:list[str] = []
            for row in listOfWords:
                word = row[0]
                meaning1 = row[1]
                meaning2 = row[2] if len(row) > 2 else None
                meaning3 = row[3] if len(row) > 3 else None
                normalizedWords.append((word,meaning1,meaning2,meaning3))

            cursor.executemany(sqlQuery,normalizedWords)
            print("/tDodano słowa do bazy danych!")

            return True
    except sqlite3.Error as e:
        print(f"Nie można dodać słów do bazy danych!: {e}")
        raise

def download_new_words_from_DB() -> DBResult:
    try:
        with dbConnection() as cursor:
            
            sqlQuery = """
            SELECT word, meaning1, meaning2, meaning3 FROM Words
            WHERE box = 0;
            """

            cursor.execute(sqlQuery)
            return DBResult(success=True, data = cursor.fetchall())
        
    except sqlite3.Error as e:
        print(f"Nie udało się pobrać słów z bazy danych: {e}")
        return DBResult(success=False, error=str(e))

def download_words_for_continuation(box:int) -> DBResult:
    try:
        with dbConnection() as cursor:

            sqlQuery = """
            SELECT word, meaning1, meaning2, meaning3,
                total_attempts,
                total_correct,
                ROUND(total_correct * 100.0 / NULLIF(total_attempts, 0), 1) AS success_rate
            FROM Words
            WHERE box >= 1
                AND box <= 5
                AND (
                total_attempts < 3
                OR
                (total_correct * 1.0 / total_attempts) >= 0.6
                )
            """

            cursor.execute(sqlQuery)
            return DBResult(success=True, data = cursor.fetchall())

    except sqlite3.Error as e:
        print(f"Nie udało się pobrać słów z bazy danych: {e}")
        return DBResult(success=False, error=str(e))

def download_difficult_words() -> DBResult:
    try:
        with dbConnection() as cursor:

            sqlQuery = """
            SELECT word, meaning1, meaning2, meaning3,
                total_attempts,
                total_correct,
                ROUND(total_correct * 100.0 / total_attempts, 1) AS success_rate
            FROM Words
            WHERE total_attempts >= 3
                AND (total_correct * 1.0 / total_attempts) < 0.6
            """

            cursor.execute(sqlQuery)
            return DBResult(success=True, data = cursor.fetchall())

    except sqlite3.Error as e:
        print(f"Nie udało się pobrać słów z bazy danych: {e}")
        return DBResult(success=False, error=str(e))

def score_learned_words(wordsToEvaluate: list[tuple[str,bool]]) -> None:

    sqlCorrect  = """
    UPDATE Words  
    SET box = CASE 
            WHEN box < 5 THEN box + 1
            ELSE 5
        END,
    total_attempts = total_attempts + 1,
    total_correct = total_correct + 1,
    last_reviewed_at = CURRENT_TIMESTAMP
    WHERE word = ?
    """
    sqlIncorrect  = """
    UPDATE Words  
    SET total_attempts = total_attempts + 1,
    total_correct = 0,
    last_reviewed_at = CURRENT_TIMESTAMP
    WHERE word = ?
    """

    correct_words = [(w,) for w, result in wordsToEvaluate if result]
    incorrect_words = [(w,) for w, result in wordsToEvaluate if not result]

    try:
        with dbConnection() as cursor:

            if correct_words:
                cursor.executemany(sqlCorrect,correct_words)
            
            if incorrect_words:
                cursor.executemany(sqlIncorrect,incorrect_words)

    except sqlite3.Error as e:
        print(f"Błąd podczas akutalizacji bazy danych: {e}")
        raise

def initialize_database() -> None:
   
    try:
        if check_if_table_exist():
            print("✓ Tabela istnieje")
        else: 
            create_table(tableName)
            print(f"Utworzono tabele! {tableName}")
    except sqlite3.Error as e:
        print(f"Błąd podczas inicjacji bazy danych: {e}")

if __name__ == "__main__":
    initialize_database()