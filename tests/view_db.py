import sqlite3

# Connect database
conn = sqlite3.connect("stock_analysis.db")

cursor = conn.cursor()

# Show all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

tables = cursor.fetchall()

print("\nTables in Database:\n")

for table in tables:
    print(table[0])

conn.close()