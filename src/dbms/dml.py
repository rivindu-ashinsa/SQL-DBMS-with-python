from __future__ import annotations

from .core import managed_connection
from .ddl import quote_identifier


def fetch_rows(table_name, connection=None, **connection_kwargs):
    with managed_connection(connection, **connection_kwargs) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {quote_identifier(table_name)}")
        columns = [column[0] for column in cursor.description or []]
        rows = cursor.fetchall()
        return columns, rows


def execute_sql(query, connection=None, **connection_kwargs):
    with managed_connection(connection, **connection_kwargs) as conn:
        cursor = conn.cursor()
        cursor.execute(query)

        if cursor.description:
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            return columns, rows, cursor.rowcount

        conn.commit()
        return [], [], cursor.rowcount


def insert_row(table_name, data, connection=None, **connection_kwargs):
    if not data:
        raise ValueError("No data was provided for insertion.")

    fields = []
    placeholders = []
    values = []
    for field_name, value in data.items():
        fields.append(quote_identifier(field_name))
        placeholders.append("%s")
        values.append(value)

    query = (
        f"INSERT INTO {quote_identifier(table_name)} "
        f"({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
    )

    with managed_connection(connection, **connection_kwargs) as conn:
        cursor = conn.cursor()
        cursor.execute(query, tuple(values))
        conn.commit()


def update_row(table_name, key_column, key_value, data, connection=None, **connection_kwargs):
    if not data:
        raise ValueError("No update values were provided.")

    set_parts = []
    values = []
    for field_name, value in data.items():
        set_parts.append(f"{quote_identifier(field_name)} = %s")
        values.append(value)

    query = (
        f"UPDATE {quote_identifier(table_name)} SET {', '.join(set_parts)} "
        f"WHERE {quote_identifier(key_column)} = %s"
    )
    values.append(key_value)

    with managed_connection(connection, **connection_kwargs) as conn:
        cursor = conn.cursor()
        cursor.execute(query, tuple(values))
        conn.commit()


def delete_row(table_name, key_column, key_value, connection=None, **connection_kwargs):
    with managed_connection(connection, **connection_kwargs) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"DELETE FROM {quote_identifier(table_name)} WHERE {quote_identifier(key_column)} = %s",
            (key_value,),
        )
        conn.commit()