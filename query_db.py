import sqlite3
conn = sqlite3.connect('database/guardian.db')
c = conn.cursor()
c.execute('SELECT incident_id, timestamp, action FROM replays ORDER BY timestamp DESC LIMIT 5')
for row in c.fetchall():
    print(row)
