import gspread, random
from dataclasses import dataclass
from typing import Optional
from google.oauth2.service_account import Credentials
from gspread.exceptions import APIError, SpreadsheetNotFound

from sql_conn import  add_word_to_main_db, check_if_google_sheet_updated, download_words_from_DB,score_learned_words

scopes:list[str] = ["https://www.googleapis.com/auth/spreadsheets"]
sheetID = "1SEylIRcFcGVEcBMnGhRyeCMhphbjbIFaWT_OYKdvCOk"

creds = Credentials.from_service_account_file("credentials.json", scopes = scopes)
client = gspread.authorize(creds)

sheet = client.open_by_key(sheetID)

worksheets = [sheet.worksheet("Strona1"),sheet.worksheet("Strona2")]


@dataclass 
class Results():
    success: bool
    data: Optional[str] = None
    error: Optional[str] = None

    @property
    def has_data(self) -> bool:
        if self.data is int:
            return self.data is not None and self.data > 0
        else:
            return self.data is not None and len(self.data) > 0

def download_from_googleSheets() -> list[str]: #pobieranie słówek z google sheet
    try:
        record:list[str] = []
        for sh in worksheets:
            record.extend(sh.get_all_values())
        examine = check_if_sheet_filled_correctly(record)
        if examine:
            return Results(success=True, data = record)
        
    except APIError as e:
        print(f"Błąd API Google Sheets: {e}")
        return Results(success=False, error= str(e))
    
    except SpreadsheetNotFound:
        print("Nie znaleziono arkusza")
        return Results(success=False, error= str(e))

def check_if_sync_required(updateRequired:bool = False) -> None: #sprawdzanie czy wymagana jest synchronizacja słów z google sheet

    sheetResults = download_from_googleSheets()
    
    if sheetResults.success:
        if sheetResults.has_data:
            print("Pobrano słowa z arkusza google")
        else:
            print("Brak słów w arkuszu")
    else:
        print(f"{sheetResults.error}")

    dbResult = check_if_google_sheet_updated()

    if dbResult.success:
        if dbResult.has_data:
            print("Pobrano słowa z bazy danych")
        else:
            print("Brak słów w arkuszu")
    else:
        print(f"{dbResult.error}")

    if sheetResults.success and dbResult.success:
        if len(sheetResults.data) > dbResult.data or dbResult.data == 0 or updateRequired:
            add_word_to_main_db(sheetResults.data)

def check_if_sheet_filled_correctly(listOfWords:list[str]) -> bool:   #Sprawdzanie czy arkusz google został poprawnie wypełniony
    for row in listOfWords:
        word = row[0]
        meaning1 = row[1]
        meaning2 = row[2] if len(row) > 2 and row[2] else None
        meaning3 = row[3] if len(row) > 3 and row[3] else None
    
        if not word and not meaning1:
            raise ValueError("Kolumna 1 i 2 są obowiązkowe")
        
        if meaning3 and not meaning2:
            raise ValueError("Kolumna 3 nie może istnieć bez kolumny 2")

    return True

def normalize_spaces(text: str) -> str: #czyszczenie whitespaceów z google sheet jeżeli jakieś przypadkie by się pojawiły
    return ' '.join(text.split())

def start_learning(wordsList:tuple[str],wordsQuantity:int) -> None: #nauka 
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
                meaning = input(f"Podaj wszystkie znaczenia ({len(correctMeanings)}):  ").strip().lower()
                
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
            meaning = normalize_spaces(input("Podaj znaczenie: ").strip().lower())

            if meaning == correctMeanings[0]:
                score += 1        
                wordsToEvaluate.append((el[0],True))
            else:
                wordToPractice.append(el[0])
                wordsToEvaluate.append((el[0],False))
        
    score_learned_words(wordsToEvaluate)

    print(f"Twój wynik to: {score}/{wordsQuantity}")

    if len(wordToPractice) != 0: 
        print(f"Słowa, które musisz powtórzyć to: {wordToPractice}")
    else:
        print("Gratulacje, możesz iść dalej!")

def main(scenario:int = 0) -> None: 
    
    while (True):
        quantity_input = input("Wybierz ilość słów do powtórzenia:  ") 

        if not quantity_input:
            print("To pole nie może być puste!")
            continue

        try:
            quantity = int(quantity_input)
        except ValueError:
            print("Wpisana wartość musi być liczbą całkowitą")
            continue

        if  quantity <= 0 or quantity > 100 :
            print("Podaj poprawną wartość z zakresu od 1 do 100")
            continue

        words = download_words_from_DB(scenario)
        if len(words.data) == 0:
            print("Nie można uruchomić programu, nie udało się pobrać słów z bazy danych  ")
            break
        else:
            start_learning(words.data,quantity)
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
            print("Podaj poprawną wartość z zakresu od 1 do 4")
            continue
        
        if userChoise == 1:
            check_if_sync_required(True)
            break

        if userChoise == 2:
            main(0)
            break

        # if userChoise == 3:
        #     main(1)
        #     break

        # if userChoise == 4:
        #     main(2)
        #     break

        if userChoise == 5:
            break

if __name__ == "__main__":
    choose_program()


    


