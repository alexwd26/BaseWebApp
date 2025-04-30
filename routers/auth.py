# routers/auth.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from db import get_db
from passlib.hash import bcrypt
import jwt
import datetime
import mysql.connector

router = APIRouter()

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: int = 3600):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str  # admin, waiter, customer, motoboy

class LoginRequest(BaseModel):
    username: str
    password: str

class RefreshRequest(BaseModel):
    token: str

@router.post("/register")
def register_user(data: RegisterRequest):
    hashed_password = bcrypt.hash(data.password)
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
            (data.username, hashed_password, data.role)
        )
        conn.commit()
        return {"message": "User registered successfully"}
    except mysql.connector.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    finally:
        cursor.close()
        conn.close()

@router.post("/login")
def login(data: LoginRequest):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (data.username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user or not bcrypt.verify(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user["username"], "role": user["role"]})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/refresh")
def refresh_token(data: RefreshRequest):
    try:
        payload = jwt.decode(data.token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")
        new_token = create_access_token({"sub": username, "role": role})
        return {"access_token": new_token, "token_type": "bearer"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
