from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class OrderRequest(BaseModel):
    order_type: str  # 'dine-in' or 'delivery'
    table_number: int | None = None
    address: str | None = None
    items: str
