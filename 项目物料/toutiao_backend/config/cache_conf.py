import json
from typing import Any

import redis.asyncio as redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 1  # 用 db1, 避免和若依(ry-vue)在 db0 的缓存混在一起


# 创建 Redis 的连接对象
redis_client = redis.Redis(
    host=REDIS_HOST,  # Redis 服务器的主机地址
    port=REDIS_PORT,  # Redis 端口号
    db=REDIS_DB,  # Redis 数据库编号，0~15
    decode_responses=True  # 是否将字节数据解码为字符串
)

async def get_cache(key: str) -> Any:
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败: {e}")
        return None

async def set_cache(key: str, value: Any, expire: int = 3600) -> bool:
    try:
        if isinstance(value, (dict,list)):
            value = json.dumps(value,ensure_ascii=False)
        await redis_client.setex(key,  expire, value)
        return True
    except Exception as e:
        print(f"设置缓存失败: {e}")
        return False

async def get_json_cache(key: str) :
    try:
        value = await redis_client.get(key)
        if value:
            return json.loads(value)
    except Exception as e:
        print(f"获取缓存失败: {e}")
        return None