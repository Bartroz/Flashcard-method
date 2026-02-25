import sqlite3
from contextlib import contextmanager

tableName:str = "Words"
dbName:str = "GermanLearning.db"


def check_if_table_exist() -> bool: #sprawdzanie czy DB istnienią - sprawdzane przy uruchomieniu

    try:
        with sqlite3.connect(dbName) as connection:
            cursor = connection.cursor()
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
    CREATE Table {tableName} (
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
        with sqlite3.connect(dbName) as connection:
            cursor = connection.cursor()
            cursor.execute(query1.format(tableName = missingTable))
            connection.commit()
    except sqlite3.Error as e:
        print(f"Błąd tworzenia tabel: {e}")
        connection.rollback()
        raise
                
def insert_word_to_DB(wordToAdd:str,
                      meaningToAdd1:str,
                      meaningToAdd2:str | None = None, 
                      meaningToAdd3:str | None= None) -> None:
    
    try:
        with sqlite3.connect(dbName) as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO Words (word,meaning1,meaning2,meaning3) VALUES (?,?,?,?)",
            (wordToAdd,meaningToAdd1,meaningToAdd2,meaningToAdd3))
            connection.commit()

    except sqlite3.Error as e:
            print(f"Nie udało się dodać słów do bazy danych. Error type: {e}")

def check_if_google_sheet_updated() -> int:
    try:
        with sqlite3.connect(dbName) as connection:
            cursor = connection.cursor()
            sqlQuery = """
            SELECT COUNT(*) FROM Words
            """

            cursor.execute(sqlQuery)
            dbLength:int = cursor.fetchone()

            return dbLength[0] if dbLength else 0
    except sqlite3.Error as e:
            print(f"Error occured : {e}")
            
def add_word_to_main_db(listOfWords:list[str]):

    sqlQuery = """
    INSERT or IGNORE INTO Words (word, meaning1, meaning2, meaning3)
    VALUES (?,?,?,?)
    """
    try:
        with sqlite3.connect(dbName) as connection:
            cursor = connection.cursor()
            normalizedWords:list[str] = []
            for row in listOfWords:
                word = row[0]
                meaning1 = row[1]
                meaning2 = row[2] if len(row) > 2 else None
                meaning3 = row[3] if len(row) > 3 else None
                normalizedWords.append((word,meaning1,meaning2,meaning3))

            cursor.executemany(sqlQuery,normalizedWords)
            connection.commit()

    except sqlite3.Error as e:
        print(f"Nie można dodać słów do bazy danych!: {e}")

def initialize_database() -> None:
   
    status = check_if_table_exist()
    if not status:
        create_table(tableName)
    else:
        print("✓ Tabela istnieje")


if __name__ == "__main__":
    initialize_database()