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
    

def convert_to_tuple(data_list):
    output_string = '('
    for i in range(len(data_list)):
        output_string += '"'
        output_string += data_list[i]
        output_string += '"'
        if i < len(data_list)-1 : 
            output_string += ","
        else:
            output_string += ")"

    return output_string

    
def non_quote_tuple(data_list):
    output_string = "("
    for i in range(len(data_list)):
        output_string += data_list[i]
        if i < len(data_list)-1:
            output_string += ','
    output_string += ")"
    return output_string


class Table:
    def __init__(self,table_name):
        self.table_name = table_name
        curser.execute(f'SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = "{self.table_name}";')
        self.c_names = []
        column_names = curser.fetchall()
        for i in column_names:
            for x in i:
                self.c_names.append(x)
        

    def table_format(self):
        curser.execute(f'SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = "{self.table_name}";')
        data = curser.fetchall()
        for i in data:
            for x in i:
                print(x)


    def insert_data(self):  
        data_row = []
        for i in range(len(self.c_names)):
            datum = input(f"{self.c_names[i]} : ")
            data_row.append(datum)
        query = f'INSERT INTO {self.table_name} {non_quote_tuple(self.c_names)} \nVALUES \n{convert_to_tuple(data_row)}'
        curser.execute(query)
        db.commit()
        db.close()
        time.sleep(1)


    def show_data(self):
        curser.execute(f'SELECT * FROM {self.table_name}')
        data = curser.fetchall()
        table = []
        table.append(self.c_names)
        for i in data:
            i = list(i)
            table.append(i)
        print(tabulate.tabulate(table,tablefmt='grid'))


    def delete_data(self):
        curser.execute(f'SELECT * FROM {self.table_name}')
        data = curser.fetchall()
        table = []
        table.append(self.c_names)
        for i in range(len(data)):
            table.append(list(data[i]))
        print(tabulate.tabulate(table,tablefmt='grid'))
        row_number = int(input("enter the row number to delete : "))
        for i in range(len(table)):
            if (table.index(table[i])) == row_number:
                print(table[i])
                primary_element = table[i][0]
                confirmation = input("confirm (y/n) : ").lower()
                if confirmation == 'y':
                    try : 
                        query = f'DELETE FROM {self.table_name} WHERE {self.c_names[0]} = "{primary_element}";'
                        curser.execute(query)
                        print("successfully removed the data")
                        db.commit()
                        db.close()    
                        time.sleep(2)
                    except mb.IntegrityError: 
                        print("foriegn key references")
                        return
                elif confirmation == 'n':
                    return
            else:
                print("row unavailable")
                return


    def update_data(self):
        curser.execute(f'SELECT * FROM {self.table_name}')
        data = curser.fetchall()
        table = []
        table.append(self.c_names)
        for i in range(len(data)):
            table.append(list(data[i]))
        print(tabulate.tabulate(table,tablefmt='grid'))
        row_number_to_update = int(input("enter the row number to be updated : "))
        p_datum_of_the_row = table[row_number_to_update][0]
        print(table[row_number_to_update])
        confirmation = input("confirm (y/n) : ").lower()
        if confirmation == "y":
            for i in range(len(self.c_names)):
                new_datum = input(f'updated data for {self.c_names[i]} : ')
                if new_datum != "":
                    query = (f'UPDATE {self.table_name} \nSET {self.c_names[i]} = "{new_datum}" \nWHERE {self.c_names[0]} = "{p_datum_of_the_row}";')
                    curser.execute(query)
                else:
                    pass
        elif confirmation == "n":
            return

class C_query : 
    def write_query(self,query):
        try : 
            curser.execute(query)   
            print("query executed seccussfully ! ")
        except:
            print('plz check your query again ! ')
            print(Error)