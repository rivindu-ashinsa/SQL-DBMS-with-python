from __future__ import annotations

import os

import mariadb
from dotenv import load_dotenv

load_dotenv()


def get_connection(
    host: str | None = None,
    user: str | None = None,
    password: str | None = None,
    database: str | None = None,
):
    """Create a MariaDB connection using explicit values or environment defaults."""

    return mariadb.connect(
        host=host or os.getenv("DB_HOST", "localhost"),
        user=user or os.getenv("DB_USER", "root"),
        password=password if password is not None else os.getenv("DB_PASS", ""),
        database=database if database is not None else os.getenv("DB_NAME", ""),
    )