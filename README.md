# SQL Database Management System in Python

A local SQL database workbench built with Python and Kivy. The application provides a polished desktop UI for managing MariaDB/MySQL-style databases on your machine, including database creation, table creation, row inserts, updates, deletes, and custom SQL execution.

---

## Features

### Data Definition Language (DDL)
- Create a new database.
- Create a new table from SQL column definitions.
- Drop existing tables.

### Data Manipulation Language (DML)
- Browse rows from a table.
- Insert new records with `column=value` pairs.
- Update existing rows by key column.
- Delete rows by key column.

### SQL Console
- Run custom SQL statements and inspect tabular results in-app.

---

## Prerequisites

- Python 3.12+ recommended
- MySQL or MariaDB running locally
- Kivy for the desktop UI
- Python libraries: `kivy`, `mariadb`, `python-dotenv`

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
   pip install -r requirements.txt
   ```

4. **Database Credentials:**
   - The application assumes `localhost`, `root` user, and no password by default.
   - To use different credentials, modify the `conn_dict` in `sql_ddl.py` and `sql_dml.py` accordingly.

---

## Running the Application

1. **Ensure your database server (MySQL/MariaDB) is running.**
2. **Start the Kivy dashboard:**
   ```bash
   python src/main.py
   ```
3. **Use the sidebar to move between:**
   - Connection setup.
   - DDL tools for databases and tables.
   - DML tools for inserts, updates, deletes, and browsing.
   - The SQL console for custom queries.

---

## File Structure

```
SQL-DBMS-with-python/
├── README.md
├── requirements.txt
└── src/
   ├── main.py        # Kivy launcher
   ├── gui.py         # Kivy dashboard UI
   └── dbms/          # Reusable database operations
```

---

## Usage

- Start the app with `python src/main.py`.
- Connect to the local database server first.
- Use the DDL and DML screens for common workflows, or the SQL console for raw statements.

---

## Notes

- The UI is designed for local development and assumes a MariaDB/MySQL-compatible server is already running.
- Connection defaults are loaded from `.env` if present.
- The old terminal-based interface files were removed in favor of the Kivy dashboard.

---

## Contributing

Contributions are welcome! Feel free to fork the repository and submit pull requests to improve features, fix bugs, or add documentation.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Author

Created by Rivindu Ashinsa.
