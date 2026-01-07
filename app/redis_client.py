# import redis

# redis_client = redis.Redis(
#     host="",  # your Redis server
#     port=6379,
#     db=0,
#     decode_responses=True,
#     socket_connect_timeout=3,
#     socket_timeout=3,
# )

# # Confirm Redis connection at startup
# try:
#     redis_client.ping()
#     print("✅ Redis connected successfully")
# except Exception as e:
#     print("❌ Redis connection failed:", e)
import redis

redis_client = redis.Redis(
    host="",
    port=6379,
    db=0,
    decode_responses=True,
)


def configure_redis_cache():
    """
    Configure Redis memory and eviction policy
    (GLOBAL Redis server settings)
    """
    try:
        # Set max memory to 100 MB
        redis_client.config_set("maxmemory", "100mb")

        # Set eviction policy to LRU
        redis_client.config_set("maxmemory-policy", "allkeys-lru")

        print("✅ Redis cache memory & LRU configured")

    except Exception as e:
        print("❌ Failed to configure Redis:", e)


# Call once at startup
configure_redis_cache()
