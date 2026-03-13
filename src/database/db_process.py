import sqlite3

from .sql_queries import (
    addWordQuery,
    downloadNewWordsQuery,
    downloadWordsForContinuationQuery,
    downloadDifficultWordsQuery,
    correctWordsQuery,
    incorrectWordsQuery
)
from .models import (
    DBResult,
    dbConnection,
)

def add_word_to_main_db(listOfWords:list[str]) -> bool:
    """ Dodawanie słów z arkuszy google do lokalnej bazy danych"""

    try:
        with dbConnection() as cursor:          
            normalizedWords:list[str] = []
            for row in listOfWords:
                word = row[0]
                meaning1 = row[1]
                meaning2 = row[2] if len(row) > 2 else None
                meaning3 = row[3] if len(row) > 3 else None
                normalizedWords.append((word,meaning1,meaning2,meaning3))
            cursor.executemany(addWordQuery,normalizedWords)
            print("Dodano słowa do bazy danych!")
            print(10*("-"))
            return True
        
    except sqlite3.Error as e:
        print(f"Nie można dodać słów do bazy danych!: {e}")
        raise

def download_new_words_from_DB() -> DBResult:
    """Pobieranie słów do nauki z bazy danych, których jeszcze użytkownik nie zaczął się uczyć"""

    try:
        with dbConnection() as cursor:
            cursor.execute(downloadNewWordsQuery)
            return DBResult(success=True, data = cursor.fetchall())
        
    except sqlite3.Error as e:
        print(f"Nie udało się pobrać słów z bazy danych: {e}")
        return DBResult(success=False, error=str(e))

def download_words_for_continuation() -> DBResult:
    """Pobieranie słów do nauki z bazy danych, których użytkownik jest w trakcie nauki"""
    try:
        with dbConnection() as cursor:
            cursor.execute(downloadWordsForContinuationQuery)
            return DBResult(success=True, data = cursor.fetchall())

    except sqlite3.Error as e:
        print(f"Nie udało się pobrać słów z bazy danych: {e}")
        return DBResult(success=False, error=str(e))

def download_difficult_words() -> DBResult:
    """Pobieranie słów do nauki z bazy danych, których użytkownik nie opanował"""
    try:
        with dbConnection() as cursor:
            cursor.execute(downloadDifficultWordsQuery)
            return DBResult(success=True, data = cursor.fetchall())

    except sqlite3.Error as e:
        print(f"Nie udało się pobrać słów z bazy danych: {e}")
        return DBResult(success=False, error=str(e))

def score_learned_words(wordsToEvaluate: list[tuple[str,bool]]) -> None:
    """Ewaluacja słów z sesji nauki"""

    #Podział na słowa poprawnie i niepoprawnie wytypowane
    correct_words = [(w,) for w, result in wordsToEvaluate if result]
    incorrect_words = [(w,) for w, result in wordsToEvaluate if not result]

    try:
        with dbConnection() as cursor:

            if correct_words:
                cursor.executemany(correctWordsQuery,correct_words)
            
            if incorrect_words:
                cursor.executemany(incorrectWordsQuery,incorrect_words)
            
            print("Ewaluacja zakończona pomyślnie")
    except sqlite3.Error as e:
        print(f"Błąd podczas aktualizacji bazy danych: {e}")
        raise

