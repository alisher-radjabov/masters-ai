import sqlite3

conn = sqlite3.connect("business_data.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='business_info';")
table = cursor.fetchone()

if table:
    print("Table exists!")
else:
    print("Table does NOT exist. Run the database setup script.")

conn.close()
