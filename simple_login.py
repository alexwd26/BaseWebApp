from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import get_db
import jwt, datetime

router = APIRouter()

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

class CustomerLoginRequest(BaseModel):
    phone: str

class CustomerCompleteRequest(BaseModel):
    phone: str
    name: str
    address: str

@router.post("/start")
def start_login(data: CustomerLoginRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (data.phone,))
    exists = cursor.fetchone()

    if not exists:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
            (data.phone, "", "customer")
        )
        conn.commit()

    cursor.close()
    conn.close()
    return {"message": "Phone accepted, continue to name/address"}

@router.post("/complete")
def complete_login(data: CustomerCompleteRequest):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET password = %s WHERE username = %s",
        (f"{data.name} | {data.address}", data.phone)
    )
    conn.commit()
    cursor.close()
    conn.close()

    token = jwt.encode({
        "sub": data.phone,
        "role": "customer",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token, "token_type": "bearer"}
