import redis
import os
import json

redis_client = None

def init_redis():
    global redis_client
    # Get Redis host from env (e.g. 'localhost' or 'redis' when in docker)
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_password = os.getenv("REDIS_PASSWORD")
    
    use_ssl = "upstash.io" in redis_host.lower()
    
    try:
        redis_client = redis.Redis(
            host=redis_host, 
            port=redis_port, 
            password=redis_password,
            ssl=use_ssl,
            db=0, 
            decode_responses=True
        )
        redis_client.ping()
        print("Connected to Redis successfully.")
    except Exception as e:
        print(f"Failed to connect to Redis: {e}")
        redis_client = None

def get_cache(key: str):
    if redis_client:
        try:
            val = redis_client.get(key)
            if val:
                return json.loads(val)
        except Exception:
            pass
    return None

def set_cache(key: str, value: dict, expire_seconds: int = 900):
    if redis_client:
        try:
            redis_client.setex(key, expire_seconds, json.dumps(value))
        except Exception:
            pass

def delete_cache(key: str):
    if redis_client:
        try:
            redis_client.delete(key)
        except Exception:
            pass
