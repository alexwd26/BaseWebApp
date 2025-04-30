from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import get_db
from typing import List

router = APIRouter()

class TableStatusUpdate(BaseModel):
    status: str  # 'disponivel', 'ocupado', 'suja'

@router.get("/", response_model=List[dict])
def get_tables():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tables ORDER BY id")
    tables = cursor.fetchall()
    cursor.close()
    conn.close()
    return tables

@router.patch("/{table_id}")
def update_table_status(table_id: int, data: TableStatusUpdate):
    if data.status not in ["disponivel", "ocupado", "suja"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE tables SET status = %s WHERE id = %s", (data.status, table_id))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": f"Table {table_id} status updated to {data.status}"}
