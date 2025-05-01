from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import shutil
import os

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload-image")
def upload_image(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
        raise HTTPException(status_code=400, detail="Invalid image format")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {"message": f"Image '{file.filename}' uploaded successfully"}

@router.get("/images/{filename}")
def get_image(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)

@router.put("/{item_id}")
def update_menu_item(item_id: int, item: MenuItem):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE menu_items
        SET name=%s, description=%s, price=%s, category=%s, image=%s
        WHERE id = %s
        """,
        (item.name, item.description, item.price, item.category, item.image, item_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Menu item updated"}

