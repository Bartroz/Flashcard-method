import sqlite3

def checkIfWordExist(sqlQuery,wordToSearch:str,wordToAdd:str = None) -> None:
    global cursor
    try:
        connection = sqlite3.connect('WordsToPractice.db')
        cursor = connection.cursor()
        
        cursor.execute(sqlQuery,(wordToSearch,))
        check = cursor.fetchone()

        if not check:
            insertWordToDB(wordToAdd)
            print("Słowo nie istnieje")
        else:
            pass

        connection.commit()
        connection.close()
    except sqlite3.Error as e:
        print("Error occured: {e}")
    finally:
        if connection:
            connection.close()
            print("Connection closed")


sqlQueryIfExist:str = """
    Select word from WordsToPractice where Word = ?
    """

def insertWordToDB(valueToAdd:str):
    global cursor
    cursor.execute("INSERT INTO WordsToPractice (Word) VALUES (?)",
    (valueToAdd,))


if __name__ == "__main__":
    checkIfWordExist(sqlQueryIfExist,"jeszcze")

