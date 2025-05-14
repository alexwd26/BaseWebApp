from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from db import get_db
from typing import List, Optional, Dict
import datetime

router = APIRouter()

class Promocao(BaseModel):
    title: str
    description: Optional[str] = None
    image: Optional[str] = None
    active: Optional[bool] = True
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    discount_value: float = 0
    is_quantity_discount: bool = False
    price: float = 0
    items: List[int] = []  # New field to store item IDs

@router.get("/promocoes", response_model=List[Dict])
def list_promocoes():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT p.id, p.title, p.description, p.image, p.active,
               p.start_date, p.end_date, p.discount_value,
               p.is_quantity_discount, p.price, pi.item_id
        FROM promotions p
        LEFT JOIN promotion_items pi ON p.id = pi.promotion_id
        WHERE p.active = True
        """,
        ()
    )

    rows = cursor.fetchall()
    result: Dict[int, Dict] = {}  # Use a dictionary to store promotions by ID

    for row in rows:
        promo_id = row[0]
        item_id = row[10]

        if promo_id not in result:
            result[promo_id] = {
                "id": promo_id,
                "title": row[1],
                "description": row[2],
                "image": row[3],
                "active": bool(row[4]),
                "start_date": row[5],
                "end_date": row[6],
                "discount_value": float(row[7]) if row[7] is not None else 0.0,
                "is_quantity_discount": bool(row[8]),
                "price": float(row[9]) if row[9] is not None else 0.0,
                "items": []
            }

        if item_id is not None and item_id not in result[promo_id]["items"]:
            result[promo_id]["items"].append(item_id)

    cursor.close()
    conn.close()
    return list(result.values())

@router.post("/promocoes")
def create_promocao(promo: Promocao):
    conn = get_db()
    cursor = conn.cursor()
    
    # Insert promotion first
    cursor.execute(
        "INSERT INTO promotions (title, description, image, active, start_date, end_date, discount_value, is_quantity_discount, price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (promo.title, promo.description, promo.image, promo.active,
         promo.start_date, promo.end_date, promo.discount_value,
         promo.is_quantity_discount, promo.price)
    )
    promotion_id = cursor.lastrowid
    
    # Insert items
    if promo.items:
        item_ids = [(promotion_id, item) for item in promo.items]
        cursor.executemany(
            "INSERT INTO promotion_items (promotion_id, item_id) VALUES (%s, %s)",
            item_ids
        )
    
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Promotion created successfully"}

@router.put("/promocoes/{promo_id}")
def update_promocao(promo_id: int, promo: Promocao):
    conn = get_db()
    cursor = conn.cursor()
    
    # Update promotion
    cursor.execute(
        """
        UPDATE promotions SET title=%s, description=%s, image=%s, active=%s,
                            start_date=%s, end_date=%s, discount_value=%s,
                            is_quantity_discount=%s, price=%s WHERE id=%s
        """,
        (promo.title, promo.description, promo.image, promo.active,
         promo.start_date, promo.end_date, promo.discount_value,
         promo.is_quantity_discount, promo.price, promo_id)
    )
    
    # Clear existing items
    cursor.execute("DELETE FROM promotion_items WHERE promotion_id=%s", (promo_id,))
    
    # Insert new items
    if promo.items:
        item_ids = [(promo_id, item) for item in promo.items]
        cursor.executemany(
            "INSERT INTO promotion_items (promotion_id, item_id) VALUES (%s, %s)",
            item_ids
        )
    
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Promotion updated successfully"}

@router.delete("/promocoes/{promo_id}")
def delete_promocao(promo_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE promotions SET active = FALSE WHERE id = %s", (promo_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Promotion deactivated"}

# New endpoint to add items to a promotion after creation
@router.post("/promocoes/{promo_id}/items")
def add_promotion_items(promo_id: int, item_ids: List[int]):
    conn = get_db()
    cursor = conn.cursor()
    
    # Delete existing items (if you want to replace)
    cursor.execute("DELETE FROM promotion_items WHERE promotion_id=%s", (promo_id,))
    
    # Insert new items
    if item_ids:
        cursor.executemany(
            "INSERT INTO promotion_items (promotion_id, item_id) VALUES (%s, %s)",
            [(promo_id, item) for item in item_ids]
        )
    
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": f"{len(item_ids)} items added to promotion {promo_id}"}
