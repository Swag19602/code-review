# app/utils.py
import redis
import json
from .config import settings
import hashlib
import json

# Initialize Redis client
redis_client = redis.Redis.from_url(settings.REDIS_URL)

def store_results(task_id: str, results: dict):
    redis_client.set(task_id, json.dumps(results))

def get_task_results(task_id: str):
    data = redis_client.get(task_id)
    if data:
        return json.loads(data)
    return None

def generate_cache_key(repo_url: str, pr_number: int) -> str:
    key_string = f"{repo_url}_pr_{pr_number}"
    return hashlib.sha256(key_string.encode()).hexdigest()

def get_cached_results(repo_url: str, pr_number: int):
    cache_key = generate_cache_key(repo_url, pr_number)
    data = redis_client.get(cache_key)
    if data:
        return json.loads(data)
    return None

def set_cached_results(repo_url: str, pr_number: int, results: dict):
    cache_key = generate_cache_key(repo_url, pr_number)
    redis_client.set(cache_key, json.dumps(results), ex=3600)  # Cache for 1 hour