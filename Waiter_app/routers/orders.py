from fastapi import APIRouter
from db import get_db
from models import OrderRequest
from datetime import datetime

router = APIRouter()

@router.post("/orders")
def create_order(order: OrderRequest):
    conn = get_db()
    cursor = conn.cursor()

    # Prepare fields for insert
    fields = ["order_type", "table_number", "address", "items", "status", "created_by", "created_at", "observation"]
    values = [
        order.order_type,
        getattr(order, "table_number", None),
        getattr(order, "address", None),
        order.items,
        getattr(order, "status", "pending"),
        getattr(order, "created_by", None),
        getattr(order, "created_at", datetime.now()),
        getattr(order, "observation", None)
    ]
    placeholders = ", ".join(["%s"] * len(fields))
    query = f"INSERT INTO orders ({', '.join(fields)}) VALUES ({placeholders})"
    cursor.execute(query, values)

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
