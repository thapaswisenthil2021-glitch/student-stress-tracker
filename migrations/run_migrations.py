import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'stress_data.db')
SQL_PATH = os.path.join(BASE_DIR, 'migrations', 'create_tables.sql')

if __name__ == '__main__':
    if not os.path.exists(SQL_PATH):
        print('Migration SQL not found:', SQL_PATH)
        raise SystemExit(1)

    with open(SQL_PATH, 'r', encoding='utf-8') as f:
        sql = f.read()

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(sql)
        conn.commit()
        print('Migrations applied to', DB_PATH)
    except Exception as e:
        print('Migration failed:', e)
    finally:
        conn.close()
