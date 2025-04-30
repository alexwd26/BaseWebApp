from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from db import get_db
import jwt
import datetime

router = APIRouter()

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

class OrderRequest(BaseModel):
    order_type: str  # 'dine-in', 'delivery', 'takeout'
    table_number: Optional[int] = None
    address: Optional[str] = None
    items: str

class OrderStatusUpdate(BaseModel):
    status: str  # 'pending', 'kitchen', 'ready', 'complete'

def get_current_user(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/", status_code=201)
def create_order(order: OrderRequest):
    conn = get_db()
    cursor = conn.cursor()
    if order.order_type == "dine-in":
        cursor.execute(
            "INSERT INTO orders (order_type, table_number, items, status) VALUES (%s, %s, %s, %s)",
            (order.order_type, order.table_number, order.items, "pending")
        )
    elif order.order_type == "delivery":
        cursor.execute(
            "INSERT INTO orders (order_type, address, items, status) VALUES (%s, %s, %s, %s)",
            (order.order_type, order.address, order.items, "pending")
        )
    elif order.order_type == "takeout":
        cursor.execute(
            "INSERT INTO orders (order_type, items, status) VALUES (%s, %s, %s)",
            (order.order_type, order.items, "pending")
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid order type")

    conn.commit()
    order_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return {"order_id": order_id, "message": "Order placed successfully"}

@router.get("/{order_id}")
def get_order_by_id(order_id: int):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
    order = cursor.fetchone()
    cursor.close()
    conn.close()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("/")
def list_orders(order_type: Optional[str] = None, status: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    base_query = "SELECT * FROM orders"
    filters = []
    params = []

    if order_type:
        filters.append("order_type = %s")
        params.append(order_type)
    if status:
        filters.append("status = %s")
        params.append(status)

    if filters:
        base_query += " WHERE " + " AND ".join(filters)

    base_query += " ORDER BY created_at DESC"

    cursor.execute(base_query, tuple(params))
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    return orders

@router.patch("/{order_id}")
def update_order_status(order_id: int, update: OrderStatusUpdate, token: str = Depends(get_current_user)):
    role = token.get("role")
    if role not in ["admin", "motoboy"]:
        raise HTTPException(status_code=403, detail="Only admin or motoboy can update order status")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = %s WHERE id = %s", (update.status, order_id))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": f"Order {order_id} status updated to {update.status}"}
