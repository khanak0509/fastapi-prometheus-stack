import uuid
from fastapi import APIRouter, HTTPException, Query
from app.schemas import Product, ProductCreate
from app.db import DATABASE, track_db_query, simulate_db_work, simulate_write_error
from typing import List, Optional

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=List[Product])
async def list_products(search: Optional[str] = None, category: Optional[str] = None):
    async with track_db_query("select", "products"):
        await simulate_db_work()
        products = list(DATABASE["products"].values())
        
        # Simple search and filter logic
        if category:
            products = [p for p in products if p.category.lower() == category.lower()]
        if search:
            products = [p for p in products if search.lower() in p.name.lower()]
        return products

@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str):
    async with track_db_query("select_one", "products"):
        await simulate_db_work()
        if product_id not in DATABASE["products"]:
            raise HTTPException(status_code=404, detail="Product not found")
        return DATABASE["products"][product_id]

@router.post("/", response_model=Product)
async def create_product(product: ProductCreate):
    async with track_db_query("insert", "products"):
        await simulate_db_work(0.01, 0.05)
        # Randomly failing here helps us see if our error alerts are working
        simulate_write_error()
        
        product_id = str(uuid.uuid4())[:8]
        new_product = Product(id=product_id, **product.model_dump())
        DATABASE["products"][product_id] = new_product
        return new_product
