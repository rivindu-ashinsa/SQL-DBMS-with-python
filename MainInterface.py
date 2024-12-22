import os
import time
import sys
def animate():
    for i in range(4):
        sys.stdout.write('\rloading |')
        time.sleep(0.1)
        sys.stdout.write('\rloading /')
        time.sleep(0.1)
        sys.stdout.write('\rloading -')
        time.sleep(0.1)
        sys.stdout.write('\rloading \\')
        time.sleep(0.1)
    os.system('cls')

                                     
def ddl():
    from sql_ddl import create_db,run_db,delete_table,custom_query

    msg = """

            1. Create a table
            2. Delete a table 
            3. Create a table
            4. Create a database
            5. Custom query
            6. Main menu
"""
    print(msg)
    choice = int(input("> "))
    if choice == 1:
        db_name = input("enter the name of the database that you need to create : ")
        create_db(db_name)
        animate()
        main_menu
    elif choice == 2:
        run_db()
        table_to_delete = input("enter the name of the table you need to delete : ")
        delete_table(table_to_delete)
        animate()
        main_menu()
    elif choice == 3:
        pass
    elif choice == 4:
        pass
    elif choice == 5:
        c_query = input("enter the query here : ")
        custom_query(c_query)
        animate()
        main_menu()
    elif choice == 6:
        main_menu()


def dml():
    import sql_dml

    os.system("cls")
    msg = """

            1. Check data
            2. Insert data
            3. Delete data
            4. Update data
            5. Custom query
            6. Main menu

"""
    print(msg)
    choice = int(input("> "))
    if choice == 1:
        animate()
        table_name = input("enter the name of the table : ")
        table = sql_dml.Table(table_name)
        table.show_data()   
        choice = input("to main menu (y): ")
    elif choice == 2:
        table_name = input("enter the name of the table : ")
        table = sql_dml.Table(table_name)
        table.insert_data()
        print("Data added successfully")
        animate()
        main_menu()

    elif choice == 3:
        table_name = input("enter the name of the table : ")
        table = sql_dml.Table(table_name)
        table.delete_data()
        animate()
        main_menu()

    elif choice == 4:
        table_name = input("enter the name of the table : ")
        table = sql_dml.Table(table_name)
        table.update_data()
        animate()
        main_menu()

    elif choice == 5:
        print("Write your own query")
        custom_query = input("prompt your own query here : \n")
        c_query = sql_dml.C_query()
        c_query.write_query(custom_query)
        animate()
        main_menu()

    elif choice == 6:
        main_menu()

def main_menu():
    os.system("cls")
    print(f"{"SQL Manager with python":^50}")                    
    animate()
    main_menu = """

            1. DDL (data definition)
            2. DML (data manipulation)

    """

    print(f"{main_menu:^50}")
    main_menu_choice = input("> ")
    main_menu_choice = main_menu_choice.replace(" ","")
    if main_menu_choice == "1":
        os.system("cls")
        animate()
        ddl()
    elif main_menu_choice == "2":
        os.system("cls")
        animate()
        dml()
    elif main_menu_choice == "exit":
        print("exiting... ")
        animate()
        sys.exit()
    else:
        print("unknown")
        main_menu()

main_menu()