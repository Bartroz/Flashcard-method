import gspread, random
from sql_conn import checkIfWordExist
from google.oauth2.service_account import Credentials
from gspread.exceptions import APIError, SpreadsheetNotFound
2
scopes = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_file("credentials.json", scopes = scopes)
client = gspread.authorize(creds)

sheet_id = "1SEylIRcFcGVEcBMnGhRyeCMhphbjbIFaWT_OYKdvCOk"
sheet = client.open_by_key(sheet_id)

worksheets = [sheet.worksheet("Strona1"),sheet.worksheet("Strona2")]

list_of_dicst = []
        
def dfDB() -> list:
    record = []
 
    for sh in worksheets:
        record.extend(sh.get_all_values())
        
    return record

def download_from_database() -> list:   #pobieranie słówek z google sheet
    rows = dfDB()

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
            list_of_dicst.append((word,meaning1,meaning2,meaning3))
        elif meaning2:
            list_of_dicst.append((word,meaning1,meaning2))
        else:
            list_of_dicst.append((word,meaning1))

    return list_of_dicst

def list_shuffe() -> None: #mieszanie listy ze słowkami
    random.shuffle(list_of_dicst)


# def chooseProgram() -> None:

    # print("\n=== MENU GŁÓWNE ===")
    # print("Wybierz tryb nauki:\n")
    # print("1) Nauka nowych słówek")
    # print("2) Powtórka poznanych słów")
    # print("3) Powtórka nieopanowanych słów")

    # choice = input("\nTwój wybór (1–3): ")

    # if choice == "1":
    #     start_learning_from_scratch()
    # elif choice == "2":
    #     repe



def start_learning(wordsQuantity:int) -> None: #nauka
    list_shuffe()
    score: int = 0
    words_to_practice = []
    for i,el in enumerate(list_of_dicst[:wordsQuantity]):
        print(f"{i+1} : {el[0]}")
        meaning = input("Podaj znaczenie:  ") 
        
        if meaning.strip() == el[1].lower() or (len(el) >2 and meaning.strip() == el[2].lower()):
            score += 1
        else:
            score += 0
            words_to_practice.append(el[0])
            checkIfWordExist(el[0],el[1])


    print(f"Twój wynik to: {score}/{wordsQuantity}")

    if len(words_to_practice) != 0: 
        print(f"Słowa, które musisz powtórzyć to: {words_to_practice}")
    else:
        print("Gratulacje, możesz iść dalej!")

def main() -> None:
    download_from_database()
    quantity = int(input("Wybierz ilość słów do powtórzenia:  "))
    start_learning(quantity)


if __name__ == "__main__":
    main()

    


