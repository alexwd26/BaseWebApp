# routers/orders.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from db import get_db

router = APIRouter()

class OrderRequest(BaseModel):
    order_type: str  # 'dine-in', 'delivery', 'takeout'
    table_number: Optional[int] = None
    address: Optional[str] = None
    items: str
    role: Optional[str] = None  # added for frontend auth

class OrderStatusUpdate(BaseModel):
    status: str  # 'pending', 'kitchen', 'ready', 'complete'
    role: Optional[str] = None  # added for frontend auth

def get_max_tables():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE name = 'max_tables'")
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return int(result[0]) if result else 20

@router.post("/", status_code=201)
def create_order(order: OrderRequest):
    if order.order_type not in ["dine-in", "delivery", "takeout"]:
        raise HTTPException(status_code=400, detail="Invalid order type")

    if order.role not in ["admin", "waiter", "customer"]:
        raise HTTPException(status_code=403, detail="Only admin, waiter, or customer can place an order")

    if order.order_type == "dine-in":
        if order.table_number is None:
            raise HTTPException(status_code=400, detail="Table number is required for dine-in")
        max_tables = get_max_tables()
        if order.table_number < 1 or order.table_number > max_tables:
            raise HTTPException(status_code=400, detail=f"Table number must be between 1 and {max_tables}")

    conn = get_db()
    cursor = conn.cursor()

    query = """
        INSERT INTO orders (order_type, table_number, address, items, status)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (
        order.order_type,
        order.table_number,
        order.address,
        order.items,
        "pending"
    ))
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
def update_order_status(order_id: int, update: OrderStatusUpdate):
    """
    Update the status of an order by its ID. Authentication is not required.
    Args:
        order_id (int): The ID of the order to update.
        update (OrderStatusUpdate): The new status for the order.
    Returns:
        dict: A message indicating the update result.
    Raises:
        HTTPException: If the status is invalid.
    """
    if update.status not in ["pending", "kitchen", "ready", "complete"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = %s WHERE id = %s", (update.status, order_id))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": f"Order {order_id} status updated to {update.status}"}
