import mysql.connector
import pandas as pd

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="091267",
    database="smart_logistics"
)

cursor = connection.cursor()

df = pd.read_csv("shipment_tracking.csv")

df = df.astype(object).where(pd.notnull(df),None)

data = [
    (
        row["shipment_id"],
        row["status"],
        row["timestamp"]
    )
    for _, row in df.iterrows()
]

cursor.executemany("""
    INSERT IGNORE INTO shipment_tracking (shipment_id, status, timestamp)
    VALUES (%s, %s, %s)
""",data)

connection.commit()

print("shipment tracking inserted succesfully!")

cursor.close()
connection.close()
