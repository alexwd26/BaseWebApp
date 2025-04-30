import mysql.connector

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="orderuser",
        password="orderpass",
        database="restaurant"
    )
