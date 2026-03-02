import mysql.connector
import pandas as pd

# Connect to MySQL
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="091267",
    database="smart_logistics"
)

cursor = connection.cursor()

# Read JSON file
warehouses_df = pd.read_json("warehouses.json")

# Insert data
for _, row in warehouses_df.iterrows():
    cursor.execute("""
        INSERT INTO warehouses (warehouse_id, city, state, capacity)
        VALUES (%s, %s, %s, %s)
    """, (row['warehouse_id'], row['city'], row['state'], row['capacity']))

connection.commit()

print("Warehouses inserted successfully!")

cursor.close()
connection.close()

