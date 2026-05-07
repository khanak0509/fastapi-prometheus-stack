import time
import asyncio
import random
from contextlib import asynccontextmanager
from app.metrics import DB_QUERIES_TOTAL, DB_QUERY_DURATION_SECONDS

@asynccontextmanager
async def track_db_query(operation: str, table: str):
    start_time = time.perf_counter()
    status = "success"
    
    try:
        # Log that we're starting a query
        DB_QUERIES_TOTAL.labels(operation=operation, table=table, status="attempt").inc()
        yield
    except Exception as e:
        # Catch and flag failures
        status = "error"
        raise e
    finally:
        # Always record how long it took, even if it crashed
        duration = time.perf_counter() - start_time
        DB_QUERIES_TOTAL.labels(operation=operation, table=table, status=status).inc()
        DB_QUERY_DURATION_SECONDS.labels(operation=operation, table=table).observe(duration)

# Just a simple dict to act as our 'database' for this demo
DATABASE = {
    "users": {},
    "orders": {},
    "products": {
        "1": {"id": "1", "name": "Laptop", "category": "Electronics", "price": 999.99},
        "2": {"id": "2", "name": "Coffee Mug", "category": "Home", "price": 12.50},
    }
}

async def simulate_db_work(min_time=0.002, max_time=0.02):
    # Adds some fake latency to make the graphs look realistic
    await asyncio.sleep(random.uniform(min_time, max_time))

def simulate_write_error(probability=0.075):
    # Occasionally throws a wrench in the gears to test our error alerts
    if random.random() < probability:
        raise Exception("Database write failure (simulated)")
