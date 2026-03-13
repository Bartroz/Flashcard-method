import logging,sys
from src.database.db_validation import initialize_database
from src.learning.study import choose_program

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )

def main():
    setup_logging()
    initialize_database()
    try:
        choose_program()
    except KeyboardInterrupt:
        print("\nZakończono działanie programu.")
        sys.exit(0)
        

if __name__ == "__main__":
    main()