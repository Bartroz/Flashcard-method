from sql_conn import add_word_to_main_db, check_if_google_sheet_updated
from google_sheet_con import download_from_database, split_data_to_rows


def operationsOnDB():
    googleSheetLength = download_from_database()
    listOfWords = split_data_to_rows()
    dbLength = check_if_google_sheet_updated()
    if dbLength == 0 or dbLength is None:
        add_word_to_main_db(listOfWords)

if __name__ == "__main__":
    operationsOnDB()
