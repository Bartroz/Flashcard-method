import gspread, random
from sql_conn import check_if_word_exist
from google.oauth2.service_account import Credentials
from gspread.exceptions import APIError, SpreadsheetNotFound

scopes:list[str] = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_file("credentials.json", scopes = scopes)
client = gspread.authorize(creds)

sheetID = "1SEylIRcFcGVEcBMnGhRyeCMhphbjbIFaWT_OYKdvCOk"
sheet = client.open_by_key(sheetID)

worksheets = [sheet.worksheet("Strona1"),sheet.worksheet("Strona2")]

listOfDicst:list[str] = []
        
def download_from_database() -> tuple[list,int]: #pobieranie słówek z google sheet
    record:list[str] = []
 
    for sh in worksheets:
        record.extend(sh.get_all_values())
    
    wordsQuantity:int = len(record)

    return record,wordsQuantity

def split_data_to_rows() -> list:   #Rodzielanie poszczególnych słówek z arkusza google na poszczególne miejsca w słowniku
    rows,length = download_from_database()
    randomNumbers: list[int] = []

    for i in range(0,5): #Generowanie 5 losowych cyfr
        randomNumbers.append(random.randrange(1, length))

    for row in rows:
        word = row[0]
        meaning1 = row[1]
        if len(row) > 2 and len(row[2]) != 0:
            meaning2 = row[2]
        else:
            meaning2 = None

            if len(row) > 3 and len(row[3]) != 0:
                meaning3 = row[3]
            else:
                meaning3 = None
    
        if not word and not meaning1:
            raise ValueError("Kolumna 1 i 2 są obowiązkowe")
        
        if meaning3 and not meaning2:
            raise ValueError("Kolumna 3 nie może istnieć bez kolumny 2")

        if meaning3:
            listOfDicst.append((word,meaning1,meaning2,meaning3))
        elif meaning2:
            listOfDicst.append((word,meaning1,meaning2))
        else:
            listOfDicst.append((word,meaning1))

    return listOfDicst

def list_shuffe() -> None: #mieszanie listy ze słowkami
    random.shuffle(listOfDicst)

def start_learning(wordsQuantity:int) -> None: #nauka
    list_shuffe()
    score: int = 0
    wordToPractice:list[str] = []

    for i,el in enumerate(listOfDicst[:wordsQuantity]):
        print(f"{i+1} : {el[0]}")
        correctMeanings = [m.lower() for m in el[1:] if m]
        
        if len(correctMeanings)> 1:
            choosenWord:set[str] = set()
            attempts:int = 0
            max_attempts: int = 3

            while (len(choosenWord) < len(correctMeanings)):
                meaning = input(f"Podaj wszystkie znaczenia ({len(el)}):  ").strip().lower()

                if meaning in correctMeanings:
                    if meaning not in choosenWord:
                        choosenWord.add(meaning)
                        score += 1
                    else:
                        print("Podane słowo już zostało dodane, podaj kolejne tłumaczenie ")
                        wordRepeated = True
                        attempts += 1 

                        if attempts >= max_attempts:
                            print("Nie udało się wytypować wszystkich znaczeń słowa")
                            wordToPractice.append(el[0])
                            check_if_word_exist(*el[:4])
                            break                           
                else:
                    score += 0
                    wordToPractice.append(el[0])
                    check_if_word_exist(*el[:4])

        else:   
            meaning = input("Podaj znaczenie:  ") 
            if meaning == correctMeanings[0]:
                score += 1        
            else:
                score += 0
                wordToPractice.append(el[0])
                check_if_word_exist(*el[:4])


    print(f"Twój wynik to: {score}/{wordsQuantity}")

    if len(wordToPractice) != 0: 
        print(f"Słowa, które musisz powtórzyć to: {wordToPractice}")
    else:
        print("Gratulacje, możesz iść dalej!")

def main() -> None:
    split_data_to_rows()
    quantity = int(input("Wybierz ilość słów do powtórzenia:  "))
    start_learning(quantity)


if __name__ == "__main__":
    main()

    


