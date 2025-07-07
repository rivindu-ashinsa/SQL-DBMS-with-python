# SQL Database Management System in Python

A simple, interactive SQL Database Management System implemented in Python. This tool allows users to create, manage, and manipulate SQL databases and tables through a command-line interface, supporting both Data Definition Language (DDL) and Data Manipulation Language (DML) operations. The system is compatible with MySQL/MariaDB databases and is designed to be beginner-friendly, making it easier to experiment with SQL database operations in a controlled environment.

---

## Features

### Data Definition Language (DDL)
- Create a new database.
- Create a new table.
- Delete existing tables.
- Execute custom SQL queries.

### Data Manipulation Language (DML)
- View data from tables.
- Insert new records into tables.
- Delete records from tables.
- Update existing records.
- Execute custom SQL queries.

---

## Prerequisites

- Python 3.x
- MySQL or MariaDB (recommended for local development)
- [XAMPP](https://www.apachefriends.org/index.html) (recommended) with MySQL server running
- Required Python library: `mysql-connector-python` or `mariadb` (depending on your setup)

---

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rivindu-ashinsa/SQL-DBMS-with-python.git
   ```

2. **Navigate to the project directory:**
   ```bash
   cd SQL-DBMS-with-python
   ```

3. **Install dependencies:**
   ```bash
   pip install mariadb tabulate
   # or, if you use MySQL:
   pip install mysql-connector-python tabulate
   ```

4. **Database Credentials:**
   - The application assumes `localhost`, `root` user, and no password by default.
   - To use different credentials, modify the `conn_dict` in `sql_ddl.py` and `sql_dml.py` accordingly.

---

## Running the Application

1. **Ensure your database server (MySQL/MariaDB) is running.**
2. **Start the main interface:**
   ```bash
   python MainInterface.py
   ```
3. **Follow the on-screen menu options to:**
   - Choose between DDL or DML operations.
   - Perform actions such as creating/deleting tables, inserting/updating/deleting/querying data, or running custom SQL.

---

## File Structure

```
SQL-DBMS-with-python/
├── MainInterface.py   # Main menu and program logic
├── sql_ddl.py        # DDL operations (CREATE, DROP, custom queries)
├── sql_dml.py        # DML operations (SELECT, INSERT, UPDATE, DELETE, custom queries)
├── README.md
└── (other supporting files)
```

---

## Usage

- Start the program by running `python MainInterface.py`.
- Use the interactive menu to select DDL or DML operations.
- Enter information as prompted.
- Custom SQL queries can also be run from within the interface.

---

## Notes

- The interface uses simple loading animations to enhance user experience.
- Make sure your database server is running and accessible before launching the application.
- The default setup uses no password for the database root user; for production or shared environments, change this to a more secure configuration.

---

## Contributing

Contributions are welcome! Feel free to fork the repository and submit pull requests to improve features, fix bugs, or add documentation.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Author

Created by Rivindu Ashinsa.
