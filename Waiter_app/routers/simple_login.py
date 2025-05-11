from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import get_db
import uuid
import datetime

router = APIRouter()

# In-memory token store for demo (token: expiry)
token_store = {}
TOKEN_EXPIRY_HOURS = 2

class CustomerLoginRequest(BaseModel):
    phone: str

class CustomerCompleteRequest(BaseModel):
    phone: str
    name: str
    address: str

@router.post("/simple-login/start")
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

@router.post("/simple-login/complete")
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

    # Generate a random token and store its expiry
    token = str(uuid.uuid4())
    expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRY_HOURS)
    token_store[token] = expiry

    return {"access_token": token, "token_type": "bearer"}
