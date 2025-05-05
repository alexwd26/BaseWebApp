from fastapi import APIRouter
from db import get_db
from models import OrderRequest

router = APIRouter()

@router.post("/orders")
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

@router.get("/orders/unprinted")
def get_unprinted_orders():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM orders WHERE printed = FALSE ORDER BY created_at ASC")
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    return orders
