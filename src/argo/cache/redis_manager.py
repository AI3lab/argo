from typing import Optional, Dict
import asyncio
from redis import asyncio as aioredis
from contextlib import asynccontextmanager

from argo.configs import logger
from argo.env_settings import settings



class RedisManager:
    def __init__(self):
        self._pool: Optional[aioredis.Redis] = None
        self._lock = asyncio.Lock()

    @property
    def pool(self) -> Optional[aioredis.Redis]:
        return self._pool

    def size(self) -> int:

        if self._pool and self._pool.connection_pool:
            return len(self._pool.connection_pool._available_connections) + len(
                self._pool.connection_pool._in_use_connections)
        return 0

    def in_use_size(self) -> int:

        if self._pool and self._pool.connection_pool:
            return len(self._pool.connection_pool._in_use_connections)
        return 0

    def available_size(self) -> int:

        if self._pool and self._pool.connection_pool:
            return len(self._pool.connection_pool._available_connections)
        return 0
    async def init_pool(self):
        if self._pool is None:
            async with self._lock:
                if self._pool is None:
                    if settings.REDIS_PASSWORD != "":
                        redis_url = f"redis://{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}"
                    else:
                        redis_url = f"redis://@{settings.REDIS_HOST}:{settings.REDIS_PORT}"

                    connection_pool = aioredis.ConnectionPool.from_url(
                        redis_url,
                        decode_responses=True,
                        max_connections=settings.REDIS_POOL_MAX_CONNECTIONS,
                        socket_timeout=settings.REDIS_POOL_TIMEOUT,
                        socket_connect_timeout=5.0,
                        retry_on_timeout=settings.REDIS_POOL_RETRY_ON_TIMEOUT,
                        health_check_interval=settings.REDIS_POOL_HEALTH_CHECK_INTERVAL,
                    )

                    self._pool = aioredis.Redis(
                        connection_pool=connection_pool
                    )
                    logger.info("Redis connection pool initialized")

    async def close(self):
        if self._pool:
            await self._pool.close()
            await self._pool.connection_pool.disconnect()
            self._pool = None
            logger.info("Redis connection pool closed")

    @asynccontextmanager
    async def get_connection(self):
        if self._pool is None:
            await self.init_pool()
        try:
            yield self._pool
        except aioredis.RedisError as e:
            logger.error(f"Redis operation error: {e}")
            raise
    async def ping(self) -> bool:

        async with self.get_connection() as redis:
            try:
                return await redis.ping()
            except Exception as e:
                logger.error(f"Redis ping failed: {e}")
                return False

    async def hset(self, name: str, key: str, value: str) -> bool:

        async with self.get_connection() as redis:
            try:
                return await redis.hset(name, key, value)
            except Exception as e:
                logger.error(f"Redis hset failed: {e}")
                raise

    async def hget(self, name: str, key: str) -> Optional[str]:

        async with self.get_connection() as redis:
            try:
                return await redis.hget(name, key)
            except Exception as e:
                logger.error(f"Redis hget failed: {e}")
                raise

    async def hgetall(self, name: str) -> Dict[str, str]:

        async with self.get_connection() as redis:
            try:
                return await redis.hgetall(name)
            except Exception as e:
                logger.error(f"Redis hgetall failed: {e}")
                raise

    async def hdel(self, name: str, *keys: str) -> int:

        async with self.get_connection() as redis:
            try:
                return await redis.hdel(name, *keys)
            except Exception as e:
                logger.error(f"Redis hdel failed: {e}")
                raise

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:

        async with self.get_connection() as redis:
            try:
                return await redis.set(key, value, ex=ex)
            except Exception as e:
                logger.error(f"Redis set failed: {e}")
                raise

    async def get(self, key: str) -> Optional[str]:

        async with self.get_connection() as redis:
            try:
                return await redis.get(key)
            except Exception as e:
                logger.error(f"Redis get failed: {e}")
                raise

    async def delete(self, *keys: str) -> int:

        async with self.get_connection() as redis:
            try:
                return await redis.delete(*keys)
            except Exception as e:
                logger.error(f"Redis delete failed: {e}")
                raise

    async def exists(self, *keys: str) -> int:

        async with self.get_connection() as redis:
            try:
                return await redis.exists(*keys)
            except Exception as e:
                logger.error(f"Redis exists failed: {e}")
                raise

    async def expire(self, key: str, seconds: int) -> bool:

        async with self.get_connection() as redis:
            try:
                return await redis.expire(key, seconds)
            except Exception as e:
                logger.error(f"Redis expire failed: {e}")
                raise

    async def ttl(self, key: str) -> int:

        async with self.get_connection() as redis:
            try:
                return await redis.ttl(key)
            except Exception as e:
                logger.error(f"Redis ttl failed: {e}")
                raise
