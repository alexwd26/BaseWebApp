from fastapi import FastAPI, APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from db import get_db

router = APIRouter()


class MenuItem(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: str


class MenuItemOut(MenuItem):
    id: int



@router.get("/", response_model=List[MenuItemOut])
def list_menu_items(category: Optional[str] = Query(None)):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    if category:
        cursor.execute("SELECT * FROM menu_items WHERE category = %s", (category,))
    else:
        cursor.execute("SELECT * FROM menu_items")
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return items



@router.get("/{item_id}", response_model=MenuItemOut)
def get_menu_item(item_id: int):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM menu_items WHERE id = %s", (item_id,))
    item = cursor.fetchone()
    cursor.close()
    conn.close()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item



@router.post("/", response_model=MenuItemOut)
def create_menu_item(item: MenuItem):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO menu_items (name, description, price, category) VALUES (%s, %s, %s, %s)",
        (item.name, item.description, item.price, item.category),
    )
    conn.commit()
    item_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return {"id": item_id, **item.dict()}



@router.put("/{item_id}", response_model=MenuItemOut)
def update_menu_item(item_id: int, item: MenuItem):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE menu_items SET name=%s, description=%s, price=%s, category=%s WHERE id=%s",
        (item.name, item.description, item.price, item.category, item_id),
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"id": item_id, **item.dict()}



@router.delete("/{item_id}")
def delete_menu_item(item_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM menu_items WHERE id=%s", (item_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Item deleted"}



@router.get("/", response_model=List[MenuItem])
def get_menu_items():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, description, price, category FROM menu_items")
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return items


@router.get("/ping")
def ping_server():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "details": str(e)}
        

app = FastAPI()
app.include_router(router)
