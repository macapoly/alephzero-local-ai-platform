import sqlite3

db = sqlite3.connect("memory/sentinel_memory.db")

rows = db.execute(
    "SELECT id, role, content, created_at "
    "FROM messages "
    "WHERE content LIKE ?",
    ("%COBOL%",)
).fetchall()

for row in rows:
    print(row)

db.close()