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

worksheet = sheet.sheet1

word_col = worksheet.col_values(1)
meaning_col = worksheet.col_values(2)
meaning_col2 = worksheet.col_values(3)

list_of_dicst = []

def download_from_database() -> None:   #pobieranie słówek z google sheet
    for x,y,z in zip(word_col,meaning_col,meaning_col2):
        if z:
            list_of_dicst.append((x,y,z))
        else:
            list_of_dicst.append((x,y))

def list_shuffe() -> None: #mieszanie listy ze słowkami
    random.shuffle(list_of_dicst)

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
    


