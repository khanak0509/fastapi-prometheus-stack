import asyncio
import httpx
import random
import time
from typing import List

BASE_URL = "http://localhost:8000/api/v1"

async def worker(worker_id: int, duration: int, stats: dict):
    start_time = time.time()
    async with httpx.AsyncClient(timeout=10.0) as client:
        while time.time() - start_time < duration:
            # We want a mix of traffic: 60% GET (safe), 30% POST (write), 10% PATCH (update)
            dice = random.random()
            
            try:
                if dice < 0.6:
                    # Simple GET requests to warm up the graphs
                    endpoint = random.choice(["/users", "/products", "/orders"])
                    req_start = time.perf_counter()
                    resp = await client.get(f"{BASE_URL}{endpoint}")
                elif dice < 0.9:
                    # POST requests—these might trigger simulated errors in our app
                    op = random.choice(["user", "product", "order"])
                    req_start = time.perf_counter()
                    if op == "user":
                        resp = await client.post(f"{BASE_URL}/users/", json={"name": f"User {worker_id}", "email": f"user{random.randint(1,1000)}@example.com"})
                    elif op == "product":
                        resp = await client.post(f"{BASE_URL}/products/", json={"name": "Widget", "category": "Tools", "price": 19.99})
                    else:
                        # Orders need a valid user_id to succeed
                        users_resp = await client.get(f"{BASE_URL}/users/")
                        users = users_resp.json()
                        if users:
                            user_id = random.choice(users)["id"]
                            resp = await client.post(f"{BASE_URL}/orders/", json={"user_id": user_id, "items": ["1", "2"]})
                        else:
                            continue
                else:
                    # PATCH requests to update order status
                    orders_resp = await client.get(f"{BASE_URL}/orders/")
                    orders = orders_resp.json()
                    if orders:
                        order_id = random.choice(orders)["id"]
                        req_start = time.perf_counter()
                        resp = await client.patch(f"{BASE_URL}/orders/{order_id}/status", json={"status": "shipped"})
                    else:
                        continue

                latency = time.perf_counter() - req_start
                stats["total_requests"] += 1
                stats["latencies"].append(latency)
                
                if resp.status_code >= 400:
                    stats["errors"] += 1
                
            except Exception as e:
                # Catch connection errors or timeouts
                stats["errors"] += 1
                stats["total_requests"] += 1
            
            # Tiny sleep to avoid pegging the CPU too hard
            await asyncio.sleep(0.05)

async def main():
    duration = 60
    num_workers = 10
    stats = {"total_requests": 0, "errors": 0, "latencies": []}
    
    print(f"🚀 Starting load test: {num_workers} workers for {duration}s...")
    
    tasks = [worker(i, duration, stats) for i in range(num_workers)]
    await asyncio.gather(*tasks)
    
    # Calculate results
    total = stats["total_requests"]
    errors = stats["errors"]
    error_rate = (errors / total * 100) if total > 0 else 0
    avg_latency = (sum(stats["latencies"]) / len(stats["latencies"])) if stats["latencies"] else 0
    
    print("\n--- Load Test Summary ---")
    print(f"Total Requests: {total}")
    print(f"Error Rate:     {error_rate:.2f}%")
    print(f"Avg Latency:    {avg_latency:.4f}s")
    print("------------------------")

if __name__ == "__main__":
    asyncio.run(main())
