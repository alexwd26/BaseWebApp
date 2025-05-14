from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class LoginRequest(BaseModel):
    username: str
    password: str

class OrderRequest(BaseModel):
    order_type: str  # 'dine-in' or 'delivery'
    table_number: int | None = None
    address: str | None = None
    items: str

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    description = Column(String)

class Promocao(Base):
    __tablename__ = "promocoes"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    discount_percentage = Column(Float)
    start_date = Column(Date)
    end_date = Column(Date)
    
    # Relationship with items (many-to-many)
    items = relationship("Item", secondary="promocoes_items")

# Junction table for many-to-many relationship
promocoes_items = Table(
    "promocoes_items",
    Base.metadata,
    Column("promotion_id", Integer, ForeignKey("promocoes.id")),
    Column("item_id", Integer, ForeignKey("items.id"))
)
