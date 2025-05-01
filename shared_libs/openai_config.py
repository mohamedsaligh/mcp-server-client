import sqlite3
from pathlib import Path

def get_db_connection():
    db_path = Path("config/app-dev.db")
    return sqlite3.connect(db_path)

def set_openai_key(api_key: str):
    conn = get_db_connection()
    conn.execute('DELETE FROM openai_config')
    conn.execute('INSERT INTO openai_config (api_key) VALUES (?)', (api_key,))
    conn.commit()
    conn.close()

def get_openai_key() -> str:
    conn = get_db_connection()
    row = conn.execute('SELECT api_key FROM openai_config').fetchone()
    conn.close()
    return row['api_key'] if row else ""

