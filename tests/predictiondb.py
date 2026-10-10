import sqlite3

conn = sqlite3.connect("stock_analysis.db")

cursor = conn.cursor()

cursor.execute("SELECT * FROM prediction_history")

# Get column names
columns = [description[0] for description in cursor.description]

print("\nColumns:\n")
print(columns)

print("\nPrediction History:\n")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()