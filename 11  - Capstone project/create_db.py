import sqlite3

# Connect to SQLite database (creates file if not exists)
conn = sqlite3.connect("business_data.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS business_info (
        name TEXT,
        revenue REAL
    )
""")

# Insert sample data
cursor.execute("INSERT INTO business_info (name, revenue) VALUES ('Tech Solutions', 500000.00)")

# Commit and close
conn.commit()
conn.close()

print("Database created with sample data: business_data.db")