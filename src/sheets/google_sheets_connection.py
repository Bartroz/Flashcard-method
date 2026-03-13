import gspread, json
from google.oauth2.service_account import Credentials
from gspread.exceptions import APIError, SpreadsheetNotFound, WorksheetNotFound 

from src.config import CREDENTIALS_PATH, SHEET_ID, INFO_PATH
from src.database.models import DBResult
from src.database.db_validation import check_if_google_sheet_updated
from src.database.db_process import add_word_to_main_db

scopes: list[str] = ["https://www.googleapis.com/auth/spreadsheets"]

def get_sheet():
    if not SHEET_ID:
        raise EnvironmentError("Brak zmiennej SHEET_ID w pliku .env")
    
    creds = Credentials.from_service_account_file(str(CREDENTIALS_PATH), scopes=scopes)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID)

def get_worksheet_names() -> int:
    """Pobiera od użytkownika liczbę arkuszy i zwraca listę ich nazw"""
    while True:
        user_input = input("Podaj liczbę arkuszy do pobrania: ").strip()
        
        if not user_input:
            print("To pole nie może być puste!")
            continue
        
        try:
            count = int(user_input)
        except ValueError:
            print("Podana wartość musi być liczbą całkowitą!")
            continue
        
        if count <= 0:
            print("Liczba arkuszy musi być większa od 0!")
            continue
        
        return count

def download_from_googleSheets() -> DBResult:

    worksheets = json_file_service()

    try:
        record: list[str] = []

        for sh in worksheets:
            record.extend(sh.get_all_values())  

        if check_if_sheet_filled_correctly(record):
            return DBResult(success=True, data=record)
        else:
            return DBResult(success=False, error="Arkusz niepoprawnie wypełniony")

    except APIError as e:
        print(f"Błąd API Google Sheets: {e}")
        return DBResult(success=False, error=str(e))

    except SpreadsheetNotFound as e:
        print("Nie znaleziono arkusza")
        return DBResult(success=False, error=str(e))

    except WorksheetNotFound as e:
        print(f"Nie znaleziono arkusza o podanej nazwie: {e}")
        return DBResult(success=False, error=str(e))

def json_file_service(requiredSynchronize:bool = False) -> int:
    
    sheet = get_sheet()

    try:
        if requiredSynchronize:
            sheetsQuantity = get_worksheet_names()
            with open(str(INFO_PATH), "w") as f:
                json.dump({"sheetsQuantity" : sheetsQuantity}, f)
        else:
            with open(str(INFO_PATH), "r") as f:
                load = json.load(f)
                sheetsQuantity = load["sheetsQuantity"]
    except FileNotFoundError:
        print("Brak pliku sheetsQuantity.json, następuje tworzenie nowego")
        sheetsQuantity = get_worksheet_names()
        with open(str(INFO_PATH), "w") as f:
            json.dump({"sheetsQuantity" : sheetsQuantity}, f)

    return [sheet.worksheet(f"Strona{i}") for i in range(1, sheetsQuantity + 1)]

def check_if_sheet_filled_correctly(listOfWords:list[str]) -> bool:
    """ Spradzanie czy arkusz google został poprawnie wypełniony """
    

    for row in listOfWords:
        word = row[0]
        meaning1 = row[1]
        meaning2 = row[2] if len(row) > 2 and row[2] else None
        meaning3 = row[3] if len(row) > 3 and row[3] else None

    if not word or not meaning1:
        raise ValueError("Kolumna 1 i 2 są obowiązkowe")
    if meaning3 and not meaning2:
        raise ValueError("Kolumna 3 nie może istnieć bez kolumny 2")
    return True

def check_if_sync_required(updateRequired:bool = False, newSheets:bool = False) -> None:

    """ Sprawdzanie czy wymagana jest synchronizacja bazy danych z arkuszem google """

    sheetResults = download_from_googleSheets(newSheets)
    dbResult = check_if_google_sheet_updated()
    sheets_count:int =  0 
    db_count:int = 0

    db_count = dbResult.data
    
    if sheetResults.success:
        if sheetResults.has_data:
            sheets_count = len(sheetResults.data)
            print(10*("-"))
            print("Pobrano słowa z arkusza google")
        else:
            print("Brak słów w arkuszu")
    else:
        print(f"{sheetResults.error}")

    if dbResult.success:
        if dbResult.has_data:
            db_count = dbResult.data
            print("Pobrano słowa z bazy danych")
        else:
            print("Baza danych jest pusta")
    else:
        print(f"{dbResult.error}")

    if sheetResults.success and dbResult.success:
        if sheets_count > db_count or db_count == 0 or updateRequired:
            try:
                add_word_to_main_db(sheetResults.data)
            except Exception as e:
                print(f"Błąd z synchronizacją z bazą danych!: {e}")
    


