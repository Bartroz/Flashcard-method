from src.database.db_validation import initialize_database
from src.learning.study import choose_program

def main():
    initialize_database()
    choose_program()

if __name__ == "__main__":
    main()