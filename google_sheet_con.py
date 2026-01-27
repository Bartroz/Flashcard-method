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

li = worksheets[0].get_all_values()
print(li)

def dfDB() -> dict:
    google_sheet_columns = {
    "word_col": [],
    "meaning_col" : [],
    "meaning_col2" : [],
    "meaning_col3" : []
}
 
    for s in worksheets:
        google_sheet_columns["word_col"].extend(s.col_values(1))
        google_sheet_columns["meaning_col"].extend(s.col_values(2))
        google_sheet_columns["meaning_col2"].extend(s.col_values(3))
        google_sheet_columns["meaning_col3"].extend(s.col_values(4))

    return google_sheet_columns

list_of_dicst = []

def download_from_database() -> None:   #pobieranie słówek z google sheet
    table = dfDB()
    for x in table["word_col"]:
    # for x,y,z,xx in zip(table["word_col"]):
        # if z:
        #     if xx:
        #         list_of_dicst.append((x,y,z,xx))
        #     else:
        #         list_of_dicst.append((x,y,z))
        # else:
        #     list_of_dicst.append((x))
        #     print(x)

        list_of_dicst.append((x))
        print(x)
    
    # print(list_of_dicst)
    # print(len(list_of_dicst))

def list_shuffe() -> None: #mieszanie listy ze słowkami
    random.shuffle(list_of_dicst)

# def chooseProgram() -> None:
#     action = {
#         "1":""
#     }
    print("\n=== MENU GŁÓWNE ===")
    print("Wybierz tryb nauki:\n")
    print("1) Nauka nowych słówek")
    print("2) Powtórka poznanych słów")
    print("3) Powtórka nieopanowanych słów")

    choice = input("\nTwój wybór (1–3): ")



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


# if __name__ == "__main__":
    # main()
    # chooseProgram()
    # download_from_database()
    


