import mysql.connector
import pandas as pd

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="091267",
    database="smart_logistics"
)

cursor = connection.cursor()

df = pd.read_csv("costs.csv")

df = df.astype(object).where(pd.notnull(df),None)

data = [
    (
        row["shipment_id"],
        row["fuel_cost"],
        row["labor_cost"],
        row["misc_cost"]
    )
    for _, row in df.iterrows()
]

cursor.executemany("""
     INSERT IGNORE INTO costs 
    (shipment_id, fuel_cost, labor_cost, misc_cost) VALUES (%s, %s, %s, %s)""",data)

connection.commit()

print("costs inserted successfully")

cursor.close()
connection.close()