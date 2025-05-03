# tables.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from db import get_db

router = APIRouter()

class Table(BaseModel):
    table_number: int
    status: str  # 'disponivel', 'ocupado', 'suja', 'reservado'
    order_id: Optional[int] = None

class TableOut(Table):
    id: int

@router.get("/", response_model=List[TableOut])
def get_all_tables():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tables ORDER BY id")
    tables = cursor.fetchall()
    cursor.close()
    conn.close()
    return tables

@router.get("/{table_id}", response_model=TableOut)
def get_table(table_id: int):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tables WHERE id = %s", (table_id,))
    table = cursor.fetchone()
    cursor.close()
    conn.close()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return table

@router.post("/", response_model=TableOut)
def create_table(table: Table):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tables (table_number, status, order_id) VALUES (%s, %s, %s)",
        (table.table_number, table.status, table.order_id)
    )
    conn.commit()
    table_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return {"id": table_id, **table.dict()}

@router.put("/{table_id}", response_model=TableOut)
def update_table(table_id: int, table: Table):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tables SET table_number=%s, status=%s, order_id=%s WHERE id=%s",
        (table.table_number, table.status, table.order_id, table_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"id": table_id, **table.dict()}

@router.delete("/{table_id}")
def delete_table(table_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tables WHERE id=%s", (table_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Table deleted"}
