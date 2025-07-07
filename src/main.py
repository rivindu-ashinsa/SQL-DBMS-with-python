from interface.menu import main_menu
from dbms.ddl import create_database
from dbms.dml import insert_row
from utils.animation import animate

def main():
    while True:
        choice = main_menu()
        if choice == "1":
            db_name = input("Enter DB name: ")
            create_database(db_name)
        elif choice == "2":
            table = input("Table name: ")
            fields = input("Fields (comma separated): ").split(",")
            values = input("Values (comma separated): ").split(",")
            data = dict(zip([f.strip() for f in fields], [v.strip() for v in values]))
            insert_row(table, data)
        elif choice == "3":
            break

if __name__ == "__main__":
    main()