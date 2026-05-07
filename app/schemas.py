from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

# --- User Schemas ---

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: str

# --- Product Schemas ---

class ProductBase(BaseModel):
    name: str
    category: str
    price: float

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: str

# --- Order Schemas ---

class OrderCreate(BaseModel):
    user_id: str
    items: List[str]  # List of product IDs

class Order(BaseModel):
    id: str
    user_id: str
    items: List[str]
    status: str = "pending"

class OrderStatusUpdate(BaseModel):
    status: str
