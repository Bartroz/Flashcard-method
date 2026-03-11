import sys,random

from src.database.db_process import (
    score_learned_words,
    download_new_words_from_DB,
    download_words_for_continuation,
    download_difficult_words
)

from src.sheets.google_sheets_connection import check_if_sync_required

def continueLearning(lastStudyMode:int):
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
        userInput = input("").strip().lower()

        #Kontynuuj naukę
        if userInput in ["1", "tak"]:
            main(lastStudyMode)

        #Zakończ
        elif userInput in ["2", "nie"]:
            print("Zakończono działanie programu.")
            sys.exit(0)

        #Powrót do menu głównego
        elif userInput == "3":
            return
        else:
            print("Wpisz prawidłową odpowiedź")

def normalize_spaces(text: str) -> str:
    """ Usuwanie whitespaceów z google sheets """ 
    return ' '.join(text.split())

def start_learning(wordsList:tuple[str],wordsQuantity:int,scenario:int) -> None: 
    """ Rozpoczęcie nauki """

    random.shuffle(wordsList)
    score: int = 0
    max_attempts: int = 3
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
                    
                    if attempts >= max_attempts:
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
    print("1. Użyj domyślnej liczby arkuszy")
    print("2. Zmień liczbę arkuszy")
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

        if choice == 1:
            check_if_sync_required(updateRequired=True)
            break   

        elif choice == 2:
            check_if_sync_required(updateRequired=True, ask_for_sheets=True)  
            break
        
        elif choice == 3:
            return

        else:
            print("Podaj wartość 1 lub 2")

        continueLearning(lastStudyMode=3)
        break

def main(scenario:int) -> None: 
    """ Główna funkcja nauki"""

    if scenario == 0:
        words = download_new_words_from_DB()
    elif scenario == 1:
        words = download_words_for_continuation()
    elif scenario == 2:
        words = download_difficult_words() 
    elif scenario == 3:
        return
    
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
       
        start_learning(words.data,quantity,scenario)
        continueLearning(scenario)
        break

def choose_program() -> None: #wybór programu 

    print("\nWitam w aplikacji do nauki słów metodą fiszek!, wybierz swoją aktywność:")
    print("\n1. Aktualizacja bazy słów")
    print("\n2. Nauka nowych słów")
    print("\n3. Kontynuacja nauki już poznanych słów")
    print("\n4. Powtarzanie nieopanowanych słów")
    print("\n5. Zakończ")
    
    while (True):
        userChoice_input: str = input("\nWybierz swój program: ")

        if not userChoice_input:
            print("To pole nie może być puste!") 
            continue

        try:
            userChoise:int = int(userChoice_input)  
        except ValueError:
            print("Podana wartość musi być liczbą całkowitą!")
            continue

        if userChoise < 1 or userChoise > 5:
            print("Podaj poprawną wartość z zakresu od 1 do 5")
            continue
        
        if userChoise == 1:
            update_database_menu()
            break

        if userChoise == 2:
            main(0)
            break

        if userChoise == 3:
            main(1)
            break

        if userChoise == 4:
            main(2)
            break

        if userChoise == 5:
            print("Zakończono działanie programu.")
            sys.exit(0)
            break

if __name__ == "__main__":
    choose_program()