from fastapi import FastAPI, APIRouter, HTTPException, Depends, Query, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
from db import get_db
import os
import shutil

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: str
    image: Optional[str] = None
    discount: Optional[float] = None

class MenuItemCreate(MenuItemBase):
    pass

class MenuItem(MenuItemBase):
    id: int

@router.get("/", response_model=List[MenuItem])
def list_menu_items(category: Optional[str] = Query(None)):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    if category:
        cursor.execute("SELECT id, name, description, price, category, image, discount FROM menu_items WHERE category = %s", (category,))
    else:
        cursor.execute("SELECT id, name, description, price, category, image, discount FROM menu_items")
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return items

@router.get("/{item_id}", response_model=MenuItem)
def get_menu_item(item_id: int):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, description, price, category, image, discount FROM menu_items WHERE id = %s", (item_id,))
    item = cursor.fetchone()
    cursor.close()
    conn.close()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/", response_model=MenuItem)
def create_menu_item(item: MenuItemCreate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO menu_items (name, description, price, category, image, discount) VALUES (%s, %s, %s, %s, %s, %s)",
        (item.name, item.description, item.price, item.category, item.image, item.discount),
    )
    conn.commit()
    item_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return {"id": item_id, **item.dict()}

@router.post("/register-item", response_model=MenuItem)
def register_item(
    name: str = Form(...),
    description: str = Form(""),
    price: float = Form(...),
    category: str = Form(...),
    image: UploadFile = File(...),
    discount: Optional[float] = Form(None)
):
    file_path = os.path.join(UPLOAD_DIR, image.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO menu_items (name, description, price, category, image, discount) VALUES (%s, %s, %s, %s, %s, %s)",
        (name, description, price, category, image.filename, discount)
    )
    conn.commit()
    item_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return {"id": item_id, "name": name, "description": description, "price": price, "category": category, "image": image.filename, "discount": discount}

@router.put("/{item_id}", response_model=MenuItem)
def update_menu_item(item_id: int, item: MenuItemBase):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE menu_items SET name=%s, description=%s, price=%s, category=%s, image=%s, discount=%s WHERE id=%s",
        (item.name, item.description, item.price, item.category, item.image, item.discount, item_id),
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
def bulk_add_menu_items(items: List[MenuItemCreate]):
    conn = get_db()
    cursor = conn.cursor()
    for item in items:
        cursor.execute(
            "INSERT INTO menu_items (name, description, price, category, image, discount) VALUES (%s, %s, %s, %s, %s, %s)",
            (item.name, item.description, item.price, item.category, item.image, item.discount)
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