import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'db' / 'movies.db'
SCHEMA_PATH = BASE_DIR / 'db' / 'schema.sql'

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

if not SCHEMA_PATH.exists():
    print(f"Schema file not found: {SCHEMA_PATH}")
    raise SystemExit(1)

sql = SCHEMA_PATH.read_text(encoding='utf-8')

conn = sqlite3.connect(DB_PATH)
try:
    conn.executescript(sql)
    print(f"Database created/updated at: {DB_PATH}")
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cur.fetchall()]
    if tables:
        print('Tables:')
        for t in tables:
            print(f" - {t}")
    else:
        print('No tables found.')
finally:
    conn.close()
