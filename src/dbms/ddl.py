from __future__ import annotations

import re

from .core import managed_connection

IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def quote_identifier(name: str) -> str:
    if not name or not IDENTIFIER_RE.match(name):
        raise ValueError(f"Invalid SQL identifier: {name!r}")
    return f"`{name}`"


def list_databases(connection=None, **connection_kwargs):
    with managed_connection(connection, **connection_kwargs) as conn:
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES")
        return [row[0] for row in cursor.fetchall()]


def create_database(db_name, connection=None, **connection_kwargs):
    with managed_connection(connection, **connection_kwargs) as conn:
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {quote_identifier(db_name)}")
        conn.commit()


def list_tables(connection=None, **connection_kwargs):
    with managed_connection(connection, **connection_kwargs) as conn:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        return [row[0] for row in cursor.fetchall()]


def create_table(table_name, columns_definition, connection=None, **connection_kwargs):
    columns_definition = (columns_definition or "").strip()
    if not columns_definition:
        raise ValueError("Column definition text is required.")

    with managed_connection(connection, **connection_kwargs) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {quote_identifier(table_name)} ({columns_definition})"
        )
        conn.commit()


def drop_table(table_name, connection=None, **connection_kwargs):
    with managed_connection(connection, **connection_kwargs) as conn:
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {quote_identifier(table_name)}")
        conn.commit()