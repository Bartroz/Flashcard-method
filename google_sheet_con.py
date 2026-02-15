import gspread, random
from sql_conn import check_if_word_exist
from google.oauth2.service_account import Credentials
from gspread.exceptions import APIError, SpreadsheetNotFound

scopes:list[str] = ["https://www.googleapis.com/auth/spreadsheets"]
sheetID = "1SEylIRcFcGVEcBMnGhRyeCMhphbjbIFaWT_OYKdvCOk"

creds = Credentials.from_service_account_file("credentials.json", scopes = scopes)
client = gspread.authorize(creds)

sheet = client.open_by_key(sheetID)

worksheets = [sheet.worksheet("Strona1"),sheet.worksheet("Strona2")]
        
def download_from_database() -> tuple[list,int]: #pobieranie słówek z google sheet
    try:
        record:list[str] = []
        for sh in worksheets:
            record.extend(sh.get_all_values())
        return record,len(record)
    except APIError as e:
        print(f"Błąd API Google Sheets: {e}")
        return [],0
    except SpreadsheetNotFound:
        print("Nie znaleziono arkusza")
        return [],0

def split_data_to_rows() -> list:   #Rodzielanie poszczególnych słówek z arkusza google na poszczególne miejsca w słowniku
    rows,length = download_from_database()
    randomNumbers: list[int] = []
    wordsList:list[str] = []

    for i in range(0,5): #Generowanie 5 losowych cyfr
        randomNumbers.append(random.randrange(1, length))

    for row in rows:
        word = row[0]
        meaning1 = row[1]
        meaning2 = row[2] if len(row) > 2 and row[2] else None
        meaning3 = row[3] if len(row) > 3 and row[3] else None
    
        if not word and not meaning1:
            raise ValueError("Kolumna 1 i 2 są obowiązkowe")
        
        if meaning3 and not meaning2:
            raise ValueError("Kolumna 3 nie może istnieć bez kolumny 2")

        if meaning3:
            wordsList.append((word,meaning1,meaning2,meaning3))
        elif meaning2:
            wordsList.append((word,meaning1,meaning2))
        else:
            wordsList.append((word,meaning1))

    return wordsList

def start_learning(wordsList:list[str],wordsQuantity:int) -> None: #nauka
    random.shuffle(wordsList)
    score: int = 0
    max_attempts: int = 3
    wordToPractice:list[str] = []

    for i,el in enumerate(wordsList[:wordsQuantity]):
        print(f"{i+1} : {el[0]}")
        correctMeanings = [m.lower() for m in el[1:] if m]
        
        if len(correctMeanings)> 1:
            choosenWord:set[str] = set()
            attempts:int = 0
            knownMeaning:int = 0

            while (len(choosenWord) < len(correctMeanings)) :
                meaning = input(f"Podaj wszystkie znaczenia ({len(correctMeanings)}):  ").strip().lower()
                
                if not meaning:
                    print("Musisz coś wpisać")
                    continue

                if meaning in choosenWord:                       
                    print("Podane słowo już zostało dodane, podaj kolejne tłumaczenie ")
                    attempts += 1
                    
                    if attempts >= max_attempts:
                        print("Nie udało się wytypować wszystkich znaczeń słowa")
                        wordToPractice.append(el[0])
                        check_if_word_exist(*el[:4])
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
                else:
                    print(f"Znasz {knownMeaning} z {len(correctMeanings)} znaczeń")
                    wordToPractice.append(el[0])
                    check_if_word_exist(*el[:4])
                    # break
                    
        else:   
            meaning = input("Podaj znaczenie:  ") 

            if meaning == correctMeanings[0]:
                score += 1        
            else:
                wordToPractice.append(el[0])
                check_if_word_exist(*el[:4])

    print(f"Twój wynik to: {score}/{wordsQuantity}")

    if len(wordToPractice) != 0: 
        print(f"Słowa, które musisz powtórzyć to: {wordToPractice}")
    else:
        print("Gratulacje, możesz iść dalej!")

def main() -> None:
    
    while (True):
        words = split_data_to_rows()
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

        start_learning(words,quantity)
        break

if __name__ == "__main__":
    main()


    


