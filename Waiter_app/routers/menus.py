from fastapi import FastAPI, APIRouter, HTTPException, Depends, Query, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
from db import get_db
import os
import shutil

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class MenuItem(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: str
    image_url: Optional[str] = None

class MenuItemOut(MenuItem):
    id: int
    image: Optional[str] = None

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
        "INSERT INTO menu_items (name, description, price, category, image) VALUES (%s, %s, %s, %s, %s)",
        (item.name, item.description, item.price, item.category, item.image_url),
    )
    conn.commit()
    item_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return {"id": item_id, **item.dict()}

@router.post("/register-item")
def register_item(
    name: str = Form(...),
    description: str = Form(""),
    price: float = Form(...),
    category: str = Form(...),
    image: UploadFile = File(...)
):
    file_path = os.path.join(UPLOAD_DIR, image.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO menu_items (name, description, price, category, image) VALUES (%s, %s, %s, %s, %s)",
        (name, description, price, category, image.filename)
    )
    conn.commit()
    item_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return {"id": item_id, "message": f"Item '{name}' registered with image '{image.filename}'"}

@router.put("/{item_id}", response_model=MenuItemOut)
def update_menu_item(item_id: int, item: MenuItem):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE menu_items SET name=%s, description=%s, price=%s, category=%s, image=%s WHERE id=%s",
        (item.name, item.description, item.price, item.category, item.image_url, item_id),
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

@router.post("/bulk")
def bulk_add_menu_items(items: List[MenuItem]):
    conn = get_db()
    cursor = conn.cursor()
    for item in items:
        cursor.execute(
            "INSERT INTO menu_items (name, description, price, category, image) VALUES (%s, %s, %s, %s, %s)",
            (item.name, item.description, item.price, item.category, item.image_url)
        )
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": f"{len(items)} items inserted successfully"}

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
