from fastapi import APIRouter, HTTPException
from db import get_db
from models import LoginRequest

router = APIRouter()

@router.post("/login")
def login(data: LoginRequest):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (data.username, data.password))
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"user_id": user['id'], "role": user['role']}
