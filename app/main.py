from fastapi import FastAPI, Request
from pydantic import BaseModel
import time
from app.cache import get_cache, set_cache, invalidate_cache

app = FastAPI(title="FastAPI Redis Cache with Invalidation")

# ------------------------------------------------
# FAKE DATABASE (IN-MEMORY)
# ------------------------------------------------
FAKE_DB_USERS = ["Mahesh", "Kumar", "Test"]


# ------------------------------------------------
# REQUEST BODY SCHEMA
# ------------------------------------------------
class UserCreateRequest(BaseModel):
    name: str
    email: str


# ------------------------------------------------
# GET API (CACHED)
# ------------------------------------------------
@app.get("/users")
async def get_users(request: Request):
    # 1️⃣ Try Redis cache
    cached = await get_cache(request)
    if cached:
        return cached

    # 2️⃣ Simulate DB query delay
    time.sleep(2)

    data = {"users": FAKE_DB_USERS, "source": "database"}  # 🔥 dynamic data

    # 3️⃣ Store in Redis
    await set_cache(request, data, ttl=120)
    return data


# ------------------------------------------------
# POST API (ADD USER + CACHE CLEAR)
# ------------------------------------------------
@app.post("/users")
async def create_user(user: UserCreateRequest):
    # 1️⃣ Simulate DB insert
    FAKE_DB_USERS.append(user.name)
    print(f"[DB INSERT] {user.name}")

    # 2️⃣ Invalidate users cache
    invalidate_cache("cache:GET:/users*")

    return {"message": "User created successfully", "users": FAKE_DB_USERS}


# ------------------------------------------------
# PUT API (UPDATE USER + CACHE CLEAR)
# ------------------------------------------------
@app.put("/users/{user_id}")
async def update_user(user_id: int, user: UserCreateRequest):
    # 1️⃣ Simulate DB update
    if 0 <= user_id < len(FAKE_DB_USERS):
        FAKE_DB_USERS[user_id] = user.name
        print(f"[DB UPDATE] User index {user_id} updated")
    else:
        return {"error": "User not found"}

    # 2️⃣ Invalidate cache
    invalidate_cache("cache:GET:/users*")

    return {"message": "User updated", "users": FAKE_DB_USERS}


# ------------------------------------------------
# REDIS HEALTH CHECK
# ------------------------------------------------
@app.get("/health/redis")
async def redis_health():
    try:
        from app.redis_client import redis_client

        redis_client.ping()
        return {"redis": "connected"}
    except Exception as e:
        return {"redis": "down", "error": str(e)}
