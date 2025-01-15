import asyncio
from typing import List, Type

import motor
from beanie import init_beanie, Document

from argo.apps.common.model import OpLog
from argo.configs import logger
from argo.env_settings import settings


class MemoryManager:
    """
    TODO: Add DB Abstract Layer

    """
    def __init__(self):
        self.db = None
        self.client = None
        self._lock =  asyncio.Lock()

    async def init_pool(self):
        if self.db is None:
            async with self._lock:
                if self.db is None:
                    self.client = motor.motor_asyncio.AsyncIOMotorClient(
                        settings.DATABASE_URL,
                    )
                    self.db = self.client[settings.DATABASE_NAME]
                    logger.info("DB connection pool initialized")
                    await self.init_models()

    async def close(self):
        try:
            if self.client is not None:
                self.client.close()
                self.client = None
                self.db = None
                logger.info("DB connection pool closed")
        except Exception as e:
            logger.error(f"Error while closing database connection: {e}")

    async def init_models(self):
        try:
            await init_beanie(database=self.db, document_models=[
                OpLog,
            ])
            await OpLog.record("started", "")
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
            raise

    async def ping(self) -> bool:
        """
        """
        try:
            if self.client is None:
                return False
            await self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"Database ping failed: {e}")
            return False

    def size(self) -> int:

        if self.client is None:
            return 0
        return self.client.options.pool_options.max_pool_size

    async def register_models(self, models: List[Type[Document]]):
        try:
            await init_beanie(database=self.db, document_models=models)
            logger.info(f"Registered models: {models}")
        except Exception as e:
            logger.error(f"Error registering models: {e}")
            raise
