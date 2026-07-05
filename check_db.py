import sqlite3
try:
    conn = sqlite3.connect('database/guardian.db')
    c = conn.cursor()
    c.execute('SELECT * FROM replays')
    rows = c.fetchall()
    print(f"Replays count: {len(rows)}")
    for r in rows:
        print(r)
except Exception as e:
    print("Error:", e)
