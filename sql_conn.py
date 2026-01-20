import sqlite3

sqlQueryIfExist:str = """
    Select word from WordsToPractice where Word = ?
    """

sqlQueryList:list[str] = [sqlQueryIfExist]

def checkIfWordExist(sqlQuery,wordToSearch:str) -> None:
    global cursor
    try:
        with sqlite3.connect('WordsToPractice.db') as connection:
            
            cursor = connection.cursor()
            
            cursor.execute(sqlQuery,(wordToSearch,))
            check = cursor.fetchone()

            if not check:
                insertWordToDB(wordToSearch)
                print("Słowo nie istnieje, dodano do bazy danych!")
                
    except sqlite3.Error as e:
        print(f"Error occured: {e}")
    
def checkIfTableExist(tableName:str) -> bool:
    try:
        with sqlite3.connect("WordsToPractice.db") as connection:
            cursor = connection.cursor()

            sqlquery = """
            SELECT name 
            FROM sqlite_master
            WHERE type = 'table'
            AND name = ?
            """
            cursor.execute(sqlquery,(tableName,))

            mesage = cursor.fetchone()
            print(mesage)

    except sqlite3.Error as e:
        print(f"Error: {e}")


def insertWordToDB(valueToAdd:str) -> None:
    global cursor
    cursor.execute("INSERT INTO WordsToPractice (Word) VALUES (?)",
    (valueToAdd,))

checkIfTableExist("WordsToPractice")

if __name__ == "__main__":
    pass

