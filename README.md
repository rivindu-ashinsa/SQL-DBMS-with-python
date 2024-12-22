# SQL Database Management System in Python

This project is a Python-based SQL Database Management System that allows users to perform various database operations. The program is divided into the following sections:

1. **Data Definition Language (DDL)**: Create, delete, and manage databases and tables.
2. **Data Manipulation Language (DML)**: Insert, delete, update, and query data within the database.

## Features

### DDL (Data Definition Language)
- Create a new database.
- Create a new table.
- Delete existing tables.
- Execute custom SQL queries.

### DML (Data Manipulation Language)
- View data from tables.
- Insert new records into tables.
- Delete records from tables.
- Update existing records.
- Execute custom SQL queries.

## Prerequisites

Ensure you have the following installed:
- Python 3.x
- MySQL or any other database you plan to use
- Recommended to have XAMP software installed and Apache, MySQL modules on "run" state.
- Required Python libraries: `mysql-connector-python` (or equivalent library based on your database).

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```

2. Navigate to the project directory:
   ```bash
   cd sql-database-management-system
   ```

3. Install required dependencies:
   ```bash
   pip install mysql-connector-python
   ```

4. Ensure you have the necessary database credentials configured in the `sql_ddl` and `sql_dml` modules.

## Running the Application

1. Execute the main program:
   ```bash
   python main.py
   ```
2. Follow the on-screen instructions to navigate through the menu options and perform database operations.

## File Structure

- **main.py**: Contains the main interface and menu logic.
- **sql_ddl.py**: Contains DDL-related functionality.
- **sql_dml.py**: Contains DML-related functionality.

## Usage

1. Start the program by running `main.py`.
2. Choose between DDL or DML operations from the main menu.
3. Follow the prompts to execute desired operations.

## Notes

- The program uses simple animations for better user experience.
- Ensure the database server is running and accessible before running the application.

## Contributing

Contributions are welcome! Feel free to fork the repository and submit pull requests.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Author

Created by Rivindu Ashinsa.
