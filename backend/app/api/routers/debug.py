from fastapi import APIRouter
import redis
import json

router = APIRouter(prefix="/debug", tags=["debug"])

r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
)


@router.get("/redis")
def get_redis_data():
    keys = r.keys("*")
    data = {}

    for key in keys:
        key_type = r.type(key)

        if key_type == "string":
            value = r.get(key)
            try:
                data[key] = json.loads(value)
            except Exception:
                data[key] = value

        elif key_type == "list":
            data[key] = r.lrange(key, 0, -1)

        elif key_type == "hash":
            data[key] = r.hgetall(key)

        else:
            data[key] = f"Unsupported type: {key_type}"

    return {
        "total_keys": len(keys),
        "keys": keys,
        "data": data,
    }