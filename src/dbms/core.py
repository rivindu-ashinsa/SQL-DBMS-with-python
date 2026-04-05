from __future__ import annotations

from contextlib import contextmanager

from .connection import get_connection


@contextmanager
def managed_connection(connection=None, **connection_kwargs):
    if connection is not None:
        yield connection
        return

    managed = get_connection(**connection_kwargs)
    try:
        yield managed
    finally:
        managed.close()