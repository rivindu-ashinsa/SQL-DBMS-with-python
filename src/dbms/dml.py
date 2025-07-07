from .connection import get_connection

def insert_row(table, data):
    conn = get_connection()
    cur = conn.cursor()
    placeholders = ", ".join(["%s"] * len(data))
    fields = ", ".join(data.keys())
    values = tuple(data.values())
    query = f"INSERT INTO {table} ({fields}) VALUES ({placeholders})"
    cur.execute(query, values)
    conn.commit()
    cur.close()
    conn.close()