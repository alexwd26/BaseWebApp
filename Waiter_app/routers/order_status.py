from fastapi import APIRouter
from db import get_db
from typing import List

router = APIRouter()

@router.get("/order-status", response_model=List[str])
def list_order_statuses():
    return ["pending", "kitchen", "ready", "complete"]