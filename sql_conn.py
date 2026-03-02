import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass

tableName:str = "Words"
dbName:str = "GermanLearning.db"

# @dataclass
# class DBResult():


@contextmanager
def dbConnection():
    connection = sqlite3.connect(dbName)
    cursor = connection.cursor()
    try:
        yield cursor
        connection.commit()
    except sqlite3.Error as e:
        print(f"Wystąpił błąd: {e}")
        connection.rollback()
        raise
    finally:
        connection.close()


def check_if_table_exist() -> bool: #sprawdzanie czy DB istnienią - sprawdzane przy uruchomieniu

    try:
        with dbConnection() as cursor:
            sqlquery = """
            SELECT name 
            FROM sqlite_master
            WHERE type = 'table'
            AND name = ?
            """
            cursor.execute(sqlquery,(tableName,))
            if cursor.fetchone() is None:
                tableExist = False
            else: 
                tableExist = True

            return tableExist

    except sqlite3.Error as e:
        print(f"Error: {e}")
        return False
    
    
def create_table(missingTable: str) -> None: #tworzenie tabeli

    query1 = """
    CREATE Table IF NOT EXISTS {tableName} (
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
            cursor.execute(query1.format(tableName = missingTable))            
    except sqlite3.Error as e:
        print(f"Błąd tworzenia tabel: {e}")
        raise
                
def check_if_google_sheet_updated() -> int:
    try:
        with dbConnection() as cursor:

            sqlQuery = """
            SELECT COUNT(*) FROM Words
            """
            cursor.execute(sqlQuery)
            dbLength:int = cursor.fetchone()

            return dbLength[0] if dbLength else 0
    except sqlite3.Error as e:
            print(f"Error occured : {e}")
            return 0

def add_word_to_main_db(listOfWords:list[str]) -> None:

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

    except sqlite3.Error as e:
        print(f"Nie można dodać słów do bazy danych!: {e}")
        raise

def download_words_from_DB(box:int = 0) -> list[str]:
    try:
        with dbConnection() as cursor:
            
            sqlQuery = """
            SELECT word, meaning1, meaning2, meaning3 FROM Words
            WHERE box = ?;
            """

            cursor.execute(sqlQuery,(box,))
            return cursor.fetchall()
        
    except sqlite3.Error as e:
        print(f"Nie udało się pobrać słów z bazy danych: {e}")
        return []

def score_learned_words(wordsToEvaluate: list[tuple[str,bool]]) -> None:

    sqlCorrect  = """
    UPDATE WORDS
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
    UPDATE WORDS
    SET total_attempts = total_attempts + 1,
    total_correct = 0,
    last_reviewed_at = CURRENT_TIMESTAMP
    WHERE word = ?
    """

    correct_words = []
    incorrect_words = []

    for word,result in wordsToEvaluate:
        if result:
            correct_words.append((word,))
        else:
            incorrect_words.append((word,))

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
   
    status = check_if_table_exist()
    if not status:
        create_table(tableName)
    else:
        print("✓ Tabela istnieje")


if __name__ == "__main__":
    initialize_database()