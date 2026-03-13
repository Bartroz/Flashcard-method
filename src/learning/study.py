import sys,random
from enum import Enum
from src.database.db_process import (
    score_learned_words,
    download_new_words_from_DB,
    download_words_for_continuation,
    download_difficult_words
)

from src.sheets.google_sheets_connection import check_if_sync_required

class ProgramModes(Enum):
    NEW_WORDS = 0
    TO_CONTINUE = 1
    DIFFICULT_WORDS = 2

MAX_ATTEMPTS: int = 3

def continueLearning():
    """
    Funkcja wywołująca się po zakończeniu nauki, proponuje użytkownikowi 3 możliwości:

    1. Kontynuowanie nauki słów w wybranym wcześniej przez siebie trybie
    2. Zakończenie nauki i tym samym zakończenie programu
    3. Powrotu do menu wyboru programu

    """  
    toContinue:bool = False
    while True:
        print("\nCzy chcesz kontynuować?")
        print(" 1: Tak")
        print(" 2: Nie")
        print(" 3: Powrót do menu głównego")
        userInput = input("Wybierz odpowiedź: ").strip().lower()

        #Kontynuuj naukę
        if userInput in ["1", "tak"]:
            return True

        #Zakończ
        elif userInput in ["2", "nie"]:
            print("Zakończono działanie programu.")
            sys.exit(0)

        #Powrót do menu głównego
        elif userInput == "3":
            return False
        else:
            print("Wpisz prawidłową odpowiedź")

def normalize_spaces(text: str) -> str:
    """ Usuwanie whitespaceów z google sheets """ 
    return ' '.join(text.split())

def start_learning(wordsList:list[tuple],wordsQuantity:int,scenario:int) -> None: 
    """ Rozpoczęcie nauki """

    random.shuffle(wordsList)
    score: int = 0

    wordToPractice:list[str] = []
    wordsToEvaluate: list[tuple[str,bool]] = []

    for i,el in enumerate(wordsList[:wordsQuantity]):
        print(f"{i+1} : {el[0]}")
        correctMeanings = [normalize_spaces(m.lower().strip()) for m in el[1:] if m]
        
        if len(correctMeanings)> 1:
            choosenWord:set[str] = set()
            attempts:int = 0
            knownMeaning:int = 0

            while (len(choosenWord) < len(correctMeanings)) :
                meaning = normalize_spaces(input(f"Podaj wszystkie znaczenia ({len(correctMeanings)}):  ").strip().lower())
                
                if not meaning:
                    print("Musisz coś wpisać")
                    attempts += 1
                    continue

                if meaning in choosenWord:                       
                    print("Podane słowo już zostało dodane, podaj kolejne tłumaczenie ")
                    attempts += 1
                    
                    if attempts >= MAX_ATTEMPTS:
                        print("Nie udało się wytypować wszystkich znaczeń słowa")
                        wordToPractice.append(el[0])
                        break  
                    
                    continue

                choosenWord.add(meaning)

                if meaning in correctMeanings: 
                    knownMeaning += 1
                    print(f"Super! Został ci jeszcze {len(correctMeanings)- knownMeaning} znaczeń do wpisania!")
                else:
                    print("Błędne znaczenie")

            if (len(choosenWord)) == len(correctMeanings):

                if len(correctMeanings) == knownMeaning:
                    print("Gratulacje, znasz wszystkie znaczenia tego słowa!")
                    score += 1
                    wordsToEvaluate.append((el[0],True))
                else:
                    print(f"Znasz {knownMeaning} z {len(correctMeanings)} znaczeń")
                    wordToPractice.append(el[0])
                    wordsToEvaluate.append((el[0],False))
                    
        else:
            while (True):   
                meaning = normalize_spaces(input("Podaj znaczenie: ").strip().lower())

                if not meaning:
                    print("Musisz coś wpisać")
                    continue

                if meaning == correctMeanings[0]:
                    score += 1        
                    wordsToEvaluate.append((el[0],True))
                else:
                    wordToPractice.append(el[0])
                    wordsToEvaluate.append((el[0],False))
                    
                break
        
    print(f"Twój wynik to: {score}/{wordsQuantity}")

    if len(wordToPractice) != 0: 
        print(f"Słowa, które musisz powtórzyć to: {wordToPractice}")
    else:
        print("Gratulacje, możesz iść dalej!")

    score_learned_words(wordsToEvaluate)

def update_database_menu() -> None:
    """Submenu aktualizacji bazy słów - pozwala wybrać liczbę arkuszy"""
    
    print("\n--- Aktualizacja bazy słów ---")
    print("1. Zmień liczbę arkuszy")
    print("2. Aktualizuj wybrane arkusze")
    print("3. Powrotu do menu wyboru programu")

    while True:
        userInput = input("\nWybierz opcję: ").strip()

        if not userInput:
            print("To pole nie może być puste!")
            continue

        try:
            choice = int(userInput)
        except ValueError:
            print("Podana wartość musi być liczbą całkowitą!")
            continue
        
        match choice:
            case 1:
                check_if_sync_required(updateRequired=True ,newSheets=True)  
                break
            case 2:
                check_if_sync_required(updateRequired=True)
                break
            case 3:
                return
            case _:
                print("Podaj wartość 1 lub 2")
        
        continueLearning()
        break

def main(scenario:int) -> None: 
    """ Główna funkcja nauki"""

    scenarios = {
        0 : download_new_words_from_DB,
        1 : download_words_for_continuation,
        2 : download_difficult_words
    }
    
    words = scenarios[scenario]()

    if not words.success:
        print(f"Błąd pobierania słów: {words.error}")
        return

    if not words.has_data:
        print("Brak słów w tej komorze")
        return
    
    while (True):
        quantity_input = input(f"Wybierz ilość słów do powtórzenia z {len(words.data)} dostępnych:  ") 

        if not quantity_input:
            print("To pole nie może być puste!")
            continue

        try:
            quantity = int(quantity_input)
        except ValueError:
            print("Wpisana wartość musi być liczbą całkowitą")
            continue

        if  quantity <= 0 or quantity > len(words.data) :
            print(f"Podaj poprawną wartość z zakresu od 1 do {len(words.data)}")
            continue
       
        while True:
            start_learning(words.data,quantity,scenario)
            if not continueLearning():
                return      

def choose_program() -> None: #wybór programu 

    while (True):

        print("\nWitam w aplikacji do nauki słów metodą fiszek!, wybierz swoją aktywność:")
        print(" 1. Aktualizacja bazy słów")
        print(" 2. Nauka nowych słów")
        print(" 3. Kontynuacja nauki już poznanych słów")
        print(" 4. Powtarzanie nieopanowanych słów")
        print(" 5. Zakończ")

        userChoice_input: str = input("\nWybierz swój program: ")

        if not userChoice_input:
            print("To pole nie może być puste!") 
            continue

        try:
            userChoise:int = int(userChoice_input)  
        except ValueError:
            print("Podana wartość musi być liczbą całkowitą!")
            continue

        match userChoise:
            case 1:
                update_database_menu()
            case 2:
                main(ProgramModes.NEW_WORDS.value)
            case 3:
                main(ProgramModes.TO_CONTINUE.value)
            case 4:
                main(ProgramModes.DIFFICULT_WORDS.value)
            case 5:
                print("Zakończono działanie programu.")
                sys.exit(0)
            case _:
                print("Podaj poprawną wartość z zakresu od 1 do 4")
                continue

if __name__ == "__main__":
    choose_program()