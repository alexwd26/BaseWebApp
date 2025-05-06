from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel
from db import get_db
from typing import List, Optional
import datetime
from sqlalchemy.orm import Session

router = APIRouter()

# Update Pydantic models to match DB schema
class Promocao(BaseModel):
    id: int
    name: str
    description: str 
    discount_percentage: float
    start_date: datetime.date
    end_date: datetime.date
    active: bool = True
    image_url: Optional[str] = None

class PromocaoCreate(BaseModel):
    name: str
    description: str 
    discount_percentage: float
    start_date: datetime.date
    end_date: datetime.date
    item_ids: List[int]

@router.get("/promocoes", response_model=List[schemas.Promocao])
def list_promocoes(db: Session = Depends(...)):
    promocoes = db.query(models.Promocao).filter(models.Promocao.active == True).all()
    return promocoes

@router.post("/promocoes")
async def create_promocao(promo: PromocaoCreate, db: Session = Depends(...)):
    # Create new promotion
    db_promo = models.Promocao(
        name=promo.name,
        description=promo.description,
        discount_percentage=promo.discount_percentage,
        start_date=promo.start_date,
        end_date=promo.end_date,
        active=True
    )
    
    # Add items to the promotion
    items = [db.query(models.Item).filter(models.Item.id == item_id).first() 
             for item_id in promo.item_ids]
    
    if not all(items):
        raise HTTPException(status_code=404, detail="One or more items not found")
        
    db_promo.items = [item for item in items if item]
    db.add(db_promo)
    db.commit()
    db.refresh(db_promo)
    
    return schemas.Promocao.from_orm(db_promo)

@router.put("/promocoes/{promo_id}")
async def update_promocao(promo_id: int, promo: PromocaoCreate, db: Session = Depends(...)):
    db_promo = db.query(models.Promocao).filter(models.Promocao.id == promo_id).first()
    
    if not db_promo:
        raise HTTPException(status_code=404, detail="Promotion not found")
        
    # Update fields
    db_promo.name = promo.name
    db_promo.description = promo.description
    db_promo.discount_percentage = promo.discount_percentage
    db_promo.start_date = promo.start_date
    db_promo.end_date = promo.end_date
    
    # Clear existing items
    db_promo.items.clear()
    
    # Add new items
    items = [db.query(models.Item).filter(models.Item.id == item_id).first() 
             for item_id in promo.item_ids]
    
    if not all(items):
        raise HTTPException(status_code=404, detail="One or more items not found")
        
    db_promo.items.extend([item for item in items if item])
    
    db.commit()
    db.refresh(db_promo)
    
    return schemas.Promocao.from_orm(db_promo)

@router.delete("/promocoes/{promo_id}")
async def delete_promocao(promo_id: int, db: Session = Depends(...)):
    db_promo = db.query(models.Promocao).filter(models.Promocao.id == promo_id).first()
    
    if not db_promo:
        raise HTTPException(status_code=404, detail="Promotion not found")
        
    # Soft delete
    db_promo.active = False
    db.commit()
    
    return {"message": "Promotion deactivated successfully"}
