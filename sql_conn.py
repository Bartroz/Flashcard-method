import sqlite3

def check_if_table_exist() -> None: #sprawdzanie czy DB istnienią - sprawdzane przy uruchomieniu

    tableNames:list[str] = ["WordsFromGoogleSheet","LearnedWords", "WordsToPractice","DbDataInfo" ]
    existingTablesDb:list[str] = []
    notExistingTablesDb:list[str] = []
    score:int = 0

    try:
        with sqlite3.connect("GermanLearning.db") as connection:
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

def create_tables() -> None: #tworzenie tabeli

    query1 = """
    CREATE Table {tableName} (
    id INTEGER PRIMARY KEY ,
    word TEXT,
    meaning TEXT
    ) 
    """

    query2 = """
    CREATE Table {tableName} (
    id INTEGER PRIMARY KEY,
    length INT
    )
    """

    with sqlite3.connect("GermanLearning.db") as connection:
        try:
            cursor = connection.cursor()
            
            for name in missingTables:
                
                if name == "DbDataInfo":
                    cursor.execute(query2.format(tableName = name))
                else:
                    cursor.execute(query1.format(tableName = name))

            not_exist = True
        except sqlite3.Error as e:
            print(f"Error: {e}")
            
def check_if_word_exist(wordToSearch:str,meaning:str) -> None: #sprawdzanie czy słowo istnieje w DB
    global cursor
    try:
        with sqlite3.connect('GermanLearning.db') as connection:
            
            cursor = connection.cursor()
            sqlQuery:str = """
            Select word from WordsToPractice where word = ?
            """
            cursor.execute(sqlQuery,(wordToSearch,))
            check = cursor.fetchone()

            if check is None:
                insert_word_to_DB(wordToSearch,meaning)
                
    except sqlite3.Error as e:
        print(f"Error occured: {e}")

def insert_word_to_DB(wordToAdd:str,meaningToAdd:str) -> None:
    global cursor
    cursor.execute("INSERT INTO WordsToPractice (word,meaning) VALUES (?,?)",
    (wordToAdd,meaningToAdd,))
    print("Dodano słowo")

def check_if_google_sheet_updated():
    with sqlite3.connect("GermanLearning.db") as connection:
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



if __name__ == "__main__":
    (status,missingTables) = check_if_table_exist()
    if not status:
        create_tables()