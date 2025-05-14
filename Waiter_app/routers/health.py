from fastapi import APIRouter
from db import get_db

router = APIRouter()

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

@router.get("/healthz")
def health_check():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return {"status": "healthy"}
    except Exception:
        return {"status": "unhealthy"}

@router.get("/version")
def get_version():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT version FROM app_version LIMIT 1")
    version = cursor.fetchone()
    cursor.close()
    conn.close()
    return {"version": version["version"]}
