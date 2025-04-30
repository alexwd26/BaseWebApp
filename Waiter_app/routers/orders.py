from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ValidationError, field_validator
from typing import Optional, List, Annotated
from db import get_db
import mysql.connector
import datetime

router = APIRouter()


class OrderRequest(BaseModel):
    order_type: str  # 'dine-in', 'delivery', 'takeout'
    table_number: Optional[int] = None
    address: Optional[str] = None
    items: str

    @field_validator("order_type")
    def validate_order_type(cls, value):
        if value not in ["dine-in", "delivery", "takeout"]:
            raise ValueError("Invalid order type")
        return value

    @field_validator("table_number")
    def validate_table_number(cls, value, values):
        if values.get("order_type") == "dine-in" and value is None:
            raise ValueError("table_number is required for dine-in orders")
        return value

    @field_validator("address")
    def validate_address(cls, value, values):
        if values.get("order_type") == "delivery" and value is None:
            raise ValueError("address is required for delivery orders")
        return value



class OrderStatusUpdate(BaseModel):
    status: str  # 'pending', 'kitchen', 'ready', 'complete'

    @field_validator("status")
    def validate_status(cls, value):
        if value not in ["pending", "kitchen", "ready", "complete"]:
            raise ValueError("Invalid status value")
        return value



@router.post("/", status_code=201)
def create_order(order: OrderRequest, db: Annotated[mysql.connector.connection.MySQLConnection, Depends(get_db)]):
    """
    Creates a new order in the orders table.

    Args:
        order (OrderRequest): The order details.

    Returns:
        dict: The ID of the created order and a success message.
    """
    try:
        cursor = db.cursor()
        if order.order_type == "dine-in":
            cursor.execute(
                """
                INSERT INTO orders (order_type, table_number, items, status, created_at)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (order.order_type, order.table_number, order.items, "pending", datetime.datetime.now()),
            )
        elif order.order_type == "delivery":
            cursor.execute(
                """
                INSERT INTO orders (order_type, address, items, status, created_at)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (order.order_type, order.address, order.items, "pending", datetime.datetime.now()),
            )
        elif order.order_type == "takeout":
            cursor.execute(
                """
                INSERT INTO orders (order_type, items, status, created_at)
                VALUES (%s, %s, %s, %s)
                """,
                (order.order_type, order.items, "pending", datetime.datetime.now()),
            )
        conn.commit()
        order_id = cursor.lastrowid
        return {"order_id": order_id, "message": "Order placed successfully"}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to create order: {e}")
    finally:
        cursor.close()
        db.close()



@router.get("/{order_id}")
def get_order_by_id(order_id: int, db: Annotated[mysql.connector.connection.MySQLConnection, Depends(get_db)]):
    """
    Retrieves an order from the orders table by its ID.

    Args:
        order_id (int): The ID of the order to retrieve.

    Returns:
        dict: The order details, or None if not found.

    Raises:
        HTTPException (404): If the order with the given ID is not found.
        HTTPException (500): For other database errors.
    """
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        order = cursor.fetchone()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve order: {e}")
    finally:
        cursor.close()
        db.close()



@router.get("/")
def list_orders(
    order_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Annotated[mysql.connector.connection.MySQLConnection, Depends(get_db)] = None,
):
    """
    Retrieves a list of orders from the orders table, with optional filtering.

    Args:
        order_type (Optional[str], optional): Filters orders by order type. Defaults to None.
        status (Optional[str], optional): Filters orders by order status. Defaults to None.

    Returns:
        List[dict]: A list of orders, or an empty list if no matching orders are found.

    Raises:
        HTTPException (500): For database errors.
    """
    try:
        cursor = db.cursor(dictionary=True)
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

        base_query += " ORDER BY created_at DESC"  # Add a default ordering

        cursor.execute(base_query, tuple(params))
        orders = cursor.fetchall()
        return orders
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve orders: {e}")
    finally:
        cursor.close()
        db.close()



@router.patch("/{order_id}")
def update_order_status(order_id: int, update: OrderStatusUpdate, db: Annotated[mysql.connector.connection.MySQLConnection, Depends(get_db)]):
    """
    Updates the status of an order in the orders table.

    Args:
        order_id (int): The ID of the order to update.
        update (OrderStatusUpdate): The new status for the order.

    Returns:
        dict: A message indicating the successful update.

    Raises:
        HTTPException (404): If the order with the given ID is not found.
        HTTPException (500): For database errors.
    """
    try:
        cursor = db.cursor()
        cursor.execute(
            "UPDATE orders SET status = %s WHERE id = %s", (update.status, order_id)
        )
        db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Order not found")
        return {"message": f"Order {order_id} status updated to {update.status}"}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to update order status: {e}")
    finally:
        cursor.close()
        db.close()
