import uuid
from fastapi import APIRouter, HTTPException, Query
from app.schemas import User, UserCreate
from app.db import DATABASE, track_db_query, simulate_db_work, simulate_write_error
from typing import List

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[User])
async def list_users(page: int = 1, limit: int = 10):
    # Track the query and simulate some work
    async with track_db_query("select", "users"):
        await simulate_db_work()
        all_users = list(DATABASE["users"].values())
        
        # Simple slicing for pagination
        start = (page - 1) * limit
        end = start + limit
        return all_users[start:end]

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str):
    async with track_db_query("select_one", "users"):
        await simulate_db_work()
        if user_id not in DATABASE["users"]:
            # If we can't find them, 404 is the way to go
            raise HTTPException(status_code=404, detail="User not found")
        return DATABASE["users"][user_id]

@router.post("/", response_model=User)
async def create_user(user: UserCreate):
    async with track_db_query("insert", "users"):
        # Writes are a bit more expensive/slow
        await simulate_db_work(0.01, 0.05) 
        
        # This will randomly fail ~7% of the time to test our monitoring
        simulate_write_error() 
        
        user_id = str(uuid.uuid4())[:8]
        new_user = User(id=user_id, **user.model_dump())
        DATABASE["users"][user_id] = new_user
        return new_user
