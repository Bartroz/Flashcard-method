import sqlite3

tableNames:list[str] = ["WordsFromGoogleSheet","LearnedWords", "WordsToPractice","DbDataInfo" ]
dbName:str = "GermanLearning.db"

def check_if_table_exist() -> tuple[bool,list[str]]: #sprawdzanie czy DB istnienią - sprawdzane przy uruchomieniu

    existingTablesDb:list[str] = []
    notExistingTablesDb:list[str] = []
    score:int = 0

    try:
        with sqlite3.connect(dbName) as connection:
            cursor = connection.cursor()
            for name in tableNames:

                sqlquery = """
                SELECT name 
                FROM sqlite_master
                WHERE type = 'table'
                AND name = ?
                """
                cursor.execute(sqlquery,(name,))
                existingTablesDb.append(cursor.fetchone())

            for i,exist in enumerate(existingTablesDb):

                if exist is not None:
                    if exist[0] == tableNames[i]:
                        score += 1
                elif exist is None:
                    notExistingTablesDb.append(tableNames[i])
                    score += 0

            if score != len(tableNames):
                return False,notExistingTablesDb
            else:    
                return True,[]    

    except sqlite3.Error as e:
        print(f"Error: {e}")
        return True,[]
    
    finally:
        connection.commit()

def create_tables(missingTables: list[str]) -> None: #tworzenie tabeli

    query1 = """
    CREATE Table {tableName} (
    id INTEGER PRIMARY KEY NOT NULL,
    word TEXT NOT NULL,
    meaning1 TEXT,
    meaning2 TEXT,
    meaning3 TEXT
    ) 
    """

    query2 = """
    CREATE Table {tableName} (
    id INTEGER PRIMARY KEY,
    length INT
    )
    """

    with sqlite3.connect(dbName) as connection:
        try:
            cursor = connection.cursor()
            
            for name in missingTables:
                
                if name == "DbDataInfo":
                    cursor.execute(query2.format(tableName = name))
                else:
                    cursor.execute(query1.format(tableName = name))


        except sqlite3.Error as e:
            print(f"Error: {e}")
        
        finally:
            connection.commit()
            
            
def check_if_word_exist(wordToSearch:str,
                        meaning1:str, 
                        meaning2:str | None = None,
                        meaning3:str | None = None) -> None: #sprawdzanie czy słowo istnieje w DB
    try:
        with sqlite3.connect(dbName) as connection:
            
            cursor = connection.cursor()
            sqlQuery:str = """
            Select word from WordsToPractice where word = ?
            """
            cursor.execute(sqlQuery,(wordToSearch,))
            check = cursor.fetchone()

            if check is None:
                insert_word_to_DB(wordToSearch,meaning1,meaning2,meaning3)
                
    except sqlite3.Error as e:
        print(f"Nie udało się sprawdzić czy słowa istnieją w bazie danych. Error type: {e}")
    
    finally:
        connection.commit()

def insert_word_to_DB(wordToAdd:str,
                      meaningToAdd1:str,
                      meaningToAdd2:str | None = None, 
                      meaningToAdd3:str | None= None) -> None:
    
    with sqlite3.connect(dbName) as connection:
        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO WordsToPractice (word,meaning1,meaning2,meaning3) VALUES (?,?,?,?)",
            (wordToAdd,meaningToAdd1,meaningToAdd2,meaningToAdd3))
        except sqlite3.Error as e:
            print("Nie udało się dodać słów do bazy danych. Error type: {e}")
        finally:
            connection.commit()

def check_if_google_sheet_updated() -> int:
    with sqlite3.connect(dbName) as connection:
        try:
            cursor = connection.cursor()
            sqlQuery = """
            SELECT COUNT(*) FROM WordsFromGoogleSheet
            """

            cursor.execute(sqlQuery)
            dbLength:int = cursor.fetchone()

            return dbLength[0]
        except sqlite3.Error as e:
            print("Error occured : {e}")
            
        finally:
            connection.commit()

def add_word_to_main_db(listOfWords:list[str]):
    sqlQuery = """
    INSERT INTO WordsFromGoogleSheet (word, meaning1,meaning2,meaning3)
    VALUES (?,?,?,?)
    """
    with sqlite3.connect(dbName) as connection:
        try:
            cursor = connection.cursor()
            for row in listOfWords:
                cursor.execute(sqlQuery,(row[0],row[1],row[2],row[3]))
        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            connection.commit()


if __name__ == "__main__":
    (status,missingTables) = check_if_table_exist()
    if not status:
        create_tables(missingTables)