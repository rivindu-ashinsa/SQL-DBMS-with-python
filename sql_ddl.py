import mariadb as mb
from mariadb import Error
import tabulate
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

def run_db():
    global db
    print("SQL Manager with python ")  
    conn_dict = {
        'host':'localhost',
        'user':'root',
        'password':''
    }
    try:
        db = mb.connect(**conn_dict)
        db.ping()
        print("connected !")
        os.system('cls')

    except Error as e:
        print(e) 
        print("oops\nrun the xxamp application\nrun the servers")      
    curser = db.cursor()
    curser.execute('SHOW DATABASES')
    available_databases = curser.fetchall()
    available_databases_list = []

    for i in available_databases:
        for x in i:
            print(x)
            available_databases_list.append(x)
    print("\nType the name of the database if you need to work with a exsisting database and \nif the typed database doesn't exsist, \na new database with the typed name will be created !")

    db_name = input("Database Name : ")
    db_name = db_name.replace(" ","")
    if db_name in available_databases_list:
        conn_dict = {
            'host':'localhost',
            'user':'root',
            'database' : db_name,
            'password':''
        }
    else : 
        print(f"Creating a new datbase named {db_name}")
        curser.execute(f'CREATE DATABASE {db_name}')
        conn_dict = {
            'host':'localhost',
            'user':'root',
            'database' : db_name,
            'password':''
        }
    try:
        db = mb.connect(**conn_dict)
        db.ping()
        os.system('cls')
        print("connected !")

    except Error as e:
        print(e) 
        print("oops\nrun the xxamp application\nrun the servers")

    return db

curser = run_db().cursor()


def create_db(db_name):
    curser.execute(f"CREATE DATABASE {db_name}")
    db.commit()
    print("data base created successfully !")


def delete_table(table_name):
    curser.execute(f"DROP TABLE {table_name}")
    db.commit()
    print("table deleted successfully !")


def create_table(table_name):
    curser.execute('SHOW TABLES')
    available_tables = curser.fetchall()
    if table_name in available_tables:
        print("table already exists")
    else:
        output_query = f"CREATE TABLE {table_name} ("
        no_of_cols = int(input("enter the number of columns (int) : "))
        for i in range(no_of_cols):
            name_of_the_col = input("column name : ")
            dtype_of_col = input(f"data type of {name_of_the_col} : " )
            no_of_characters = int(input("number of characters : "))
            temp_line = f"\n \t {name_of_the_col} {dtype_of_col}({no_of_characters})"
            output_query += temp_line
            if i < no_of_cols - 1 : 
                output_query += ","
        output_query += f"\n )"
    print(output_query)


create_table('NewTable')





def custom_query(query):
    curser.execute(query)


create_table('new_table')