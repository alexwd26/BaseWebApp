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
