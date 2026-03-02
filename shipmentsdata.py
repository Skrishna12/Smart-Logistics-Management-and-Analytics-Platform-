import mysql.connector
import pandas as pd

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="091267",
    database="smart_logistics"
)

cursor = connection.cursor()

# Read shipments JSON
shipments_df = pd.read_json("shipments.json")

# Replace NaN with None
shipments_df = shipments_df.astype(object).where(pd.notnull(shipments_df), None)

# Prepare data for bulk insert
data = [
    (
        row['shipment_id'],
        row['order_date'],
        row['origin'],
        row['destination'],
        row['weight'],
        row['courier_id'],
        row['status'],
        row['delivery_date']
    )
    for _, row in shipments_df.iterrows()
]

print(shipments_df["shipment_id"].duplicated().sum())

cursor.executemany("""
    INSERT IGNORE INTO shipments 
    (shipment_id, order_date, origin, destination, weight, courier_id, status, delivery_date)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
""", data)

connection.commit()

print("Shipments inserted successfully!")

cursor.close()
connection.close()
