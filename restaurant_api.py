from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector

app = FastAPI()

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="orderuser",
        password="orderpass",
        database="restaurant"
    )

class LoginRequest(BaseModel):
    username: str
    password: str

class OrderRequest(BaseModel):
    order_type: str  # 'dine-in' or 'delivery'
    table_number: int | None = None
    address: str | None = None
    items: str

@app.post("/login")
def login(data: LoginRequest):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (data.username, data.password))
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"user_id": user['id'], "role": user['role']}

@app.post("/orders")
def create_order(order: OrderRequest):
    conn = get_db()
    cursor = conn.cursor()

    if order.order_type == "dine-in":
        query = "INSERT INTO orders (order_type, table_number, items) VALUES (%s, %s, %s)"
        cursor.execute(query, (order.order_type, order.table_number, order.items))
    else:
        query = "INSERT INTO orders (order_type, address, items) VALUES (%s, %s, %s)"
        cursor.execute(query, (order.order_type, order.address, order.items))

    conn.commit()
    order_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return {"status": "ok", "order_id": order_id}

@app.get("/orders/unprinted")
def get_unprinted_orders():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM orders WHERE printed = FALSE ORDER BY created_at ASC")
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    return orders
