import sqlite3

not_exist:bool = True

def checkIfWordExist(wordToSearch:str,meaning:str) -> None: #sprawdzanie czy słowo istnieje w DB
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
                insertWordToDB(wordToSearch,meaning)
            else:
                pass
                
    except sqlite3.Error as e:
        print(f"Error occured: {e}")

def insertWordToDB(wordToAdd:str,meaningToAdd:str) -> None:
    global cursor
    cursor.execute("INSERT INTO WordsToPractice (word,meaning) VALUES (?,?)",
    (wordToAdd,meaningToAdd,))
    print("Dodano słowo")

def checkIfTableExist(): #sprawdzanie czy DB istnienią - sprawdzane przy uruchomieniu

    tableNames:list[str] = ["WordsFromGoogleSheet","LearnedWords", "WordsToPractice" ]
    existingTablesDb:list[str] = []
    notExistingTablesDb:list[str] = []
    score:int = 0

    if (not_exist):
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


def createTables(): #tworzenie tabeli

    query = """
    CREATE Table {table_name} (
    id INTEGER PRIMARY KEY ,
    word TEXT,
    meaning TEXT
    ) 
    """

    with sqlite3.connect("GermanLearning.db") as connection:
        try:
            cursor = connection.cursor()
            
            for name in missingTables:
                
                cursor.execute(query.format(table_name = name))

            not_exist = True
        except sqlite3.Error as e:
            print(f"Error: {e}")
            

if __name__ == "__main__":
    (status,missingTables) = checkIfTableExist()
    if not status:
        createTables()

