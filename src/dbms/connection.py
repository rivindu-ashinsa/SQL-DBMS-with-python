import mariadb
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return mariadb.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASS", ""),
        database=os.getenv("DB_NAME", "")
    )