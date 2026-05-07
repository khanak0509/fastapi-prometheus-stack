import uuid
from fastapi import APIRouter, HTTPException, Query
from app.schemas import Order, OrderCreate, OrderStatusUpdate
from app.db import DATABASE, track_db_query, simulate_db_work, simulate_write_error
from typing import List, Optional

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/", response_model=List[Order])
async def list_orders(status: Optional[str] = None):
    async with track_db_query("select", "orders"):
        await simulate_db_work()
        orders = list(DATABASE["orders"].values())
        # Filter by status if provided
        if status:
            orders = [o for o in orders if o.status == status]
        return orders

@router.get("/{order_id}", response_model=Order)
async def get_order(order_id: str):
    async with track_db_query("select_one", "orders"):
        await simulate_db_work()
        if order_id not in DATABASE["orders"]:
            raise HTTPException(status_code=404, detail="Order not found")
        return DATABASE["orders"][order_id]

@router.post("/", response_model=Order)
async def create_order(order_data: OrderCreate):
    async with track_db_query("insert", "orders"):
        # Writing data takes a bit longer than reading
        await simulate_db_work(0.01, 0.05)
        simulate_write_error()
        
        # Guard clause: make sure the user actually exists
        if order_data.user_id not in DATABASE["users"]:
             raise HTTPException(status_code=400, detail="User does not exist")

        order_id = str(uuid.uuid4())[:8]
        new_order = Order(
            id=order_id,
            user_id=order_data.user_id,
            items=order_data.items,
            status="pending"
        )
        DATABASE["orders"][order_id] = new_order
        return new_order

@router.patch("/{order_id}/status", response_model=Order)
async def update_order_status(order_id: str, status_update: OrderStatusUpdate):
    async with track_db_query("update", "orders"):
        await simulate_db_work(0.005, 0.02)
        simulate_write_error()
        
        if order_id not in DATABASE["orders"]:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Update and return the modified order
        order = DATABASE["orders"][order_id]
        order.status = status_update.status
        return order
