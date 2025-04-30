# routers/pizzas.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from db import get_db  # Assuming db.py is in the same directory
import mysql.connector

router = APIRouter()


class PizzaRequest(BaseModel):
    name: str = Field(..., description="Name of the pizza  (e.g., Pepperoni, Margherita)")
    description: str = Field(..., description="Description of the pizza ")
    size: str = Field(..., description="Size of the pizza (e.g., small, medium, large)")
    crust: str = Field(..., description="Type of crust (e.g., thin, thick, stuffed)")
    extras: List[str] = Field(default=[], description="List of extra toppings (e.g., extra cheese, mushrooms)")



@router.post("/pizzas", status_code=201)
def add_pizza(pizza_request: PizzaRequest):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO pizzas (name, description, size, crust, extras)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (pizza_request.name, pizza_request.description, pizza_request.size, pizza_request.crust,  ','.join(pizza_request.extras)),
        )
        conn.commit()
        pizza_id = cursor.lastrowid
        return {"pizza_id": pizza_id, "message": "Pizza added successfully"}
    except mysql.connector.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Pizza name already exists")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to add pizza: {str(e)}")
    finally:
        cursor.close()
        conn.close()
