from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from db import get_db

router = APIRouter()

# -----------------
# Pydantic Schemas
# -----------------

class OptionChoice(BaseModel):
    name: str
    extra_price: float = 0.0
    display_order: Optional[int] = 0

class ItemOption(BaseModel):
    name: str
    min_choices: int = 0
    max_choices: int = 1
    display_order: Optional[int] = 0
    choices: List[OptionChoice]

class ItemOptionOut(ItemOption):
    id: int
    item_id: int
    choices: List[dict]

# -----------------
# Endpoints
# -----------------

@router.post("/{item_id}/options", response_model=List[ItemOptionOut])
def add_item_options(item_id: int, options: List[ItemOption]):
    conn = get_db()
    cursor = conn.cursor()

    result_options = []
    for option in options:
        cursor.execute(
            "INSERT INTO item_options (item_id, name, min_choices, max_choices, display_order) VALUES (%s, %s, %s, %s, %s)",
            (item_id, option.name, option.min_choices, option.max_choices, option.display_order)
        )
        option_id = cursor.lastrowid

        for choice in option.choices:
            cursor.execute(
                "INSERT INTO option_choices (option_id, name, extra_price, display_order) VALUES (%s, %s, %s, %s)",
                (option_id, choice.name, choice.extra_price, choice.display_order)
            )

        result_options.append({
            "id": option_id,
            "item_id": item_id,
            **option.dict()
        })

    conn.commit()
    cursor.close()
    conn.close()
    return result_options

@router.get("/{item_id}/options", response_model=List[ItemOptionOut])
def get_item_options(item_id: int):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM item_options WHERE item_id = %s ORDER BY display_order", (item_id,))
    options = cursor.fetchall()

    for option in options:
        cursor.execute("SELECT * FROM option_choices WHERE option_id = %s ORDER BY display_order", (option['id'],))
        option['choices'] = cursor.fetchall()

    cursor.close()
    conn.close()
    return options
