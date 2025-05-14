from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from db import get_db
from typing import List, Optional
import datetime

router = APIRouter()

class Promocao(BaseModel):
    title: str
    description: Optional[str] = None
    image: Optional[str] = None
    active: Optional[bool] = True
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None

@router.get("/promocoes", response_model=List[dict])
def list_promocoes():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM promotions WHERE active = TRUE")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

@router.post("/promocoes")
def create_promocao(promo: Promocao):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO promotions (title, description, image, active, start_date, end_date)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (promo.title, promo.description, promo.image, promo.active, promo.start_date, promo.end_date)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Promotion created successfully"}

@router.put("/promocoes/{promo_id}")
def update_promocao(promo_id: int, promo: Promocao):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE promotions
        SET title=%s, description=%s, image=%s, active=%s, start_date=%s, end_date=%s
        WHERE id = %s
        """,
        (promo.title, promo.description, promo.image, promo.active, promo.start_date, promo.end_date, promo_id)
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
