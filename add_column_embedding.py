import sqlite3

conn = sqlite3.connect("sqlite_database.db")
cursor = conn.cursor()

cursor.execute("ALTER TABLE registeredcases ADD COLUMN embedding TEXT")
conn.commit()
conn.close()

print("✅ Column 'embedding' added successfully!")
