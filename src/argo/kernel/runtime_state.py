import asyncio
import json
import os
import time
from typing import List

from fastapi import APIRouter, FastAPI, Query, Path

from argo.character.character_manager import CharacterManager
from argo.command.command_loader import CommandLoader
from argo.command.command_manager import CommandManager
from argo.command.commands import HelpCommandHandler, StatusCommandHandler, ListUsersCommandHandler, CommandContext, \
    MessageCommandHandler, LoadCharacterCommandHandler, ListAgentsCommandHandler
from argo.configs import logger
from argo.env_settings import settings
from argo.kernel.event_handler import EventHandler
from argo.kernel.schema import WebSocketMessage, MessageType
from argo.cache.redis_manager import RedisManager
from argo.memory.memory_manager import MemoryManager
from argo.websocket.websocket_manager import WebSocketManager
from argo.websocket.websocket_handler import setup_websocket



class RuntimeState:
    def __init__(self):
        self.worker_id = os.getpid()
        self.start_time = time.time()
        self._initialized = False
        self._health_check_interval = 500
        self.redis_manager = RedisManager()
        self.event_handler = EventHandler(self.redis_manager)
        self.command_manager = CommandManager()
        self.ws_manager = WebSocketManager()
        self.character_manager = CharacterManager()
        self.memory_manager = MemoryManager()

        self.routers: List[APIRouter] = []
        self.app = None

    def load_commands(self):
        logger.info("Loading commands")
        self.command_manager.register("help", HelpCommandHandler(self.command_manager))
        self.command_manager.register("status", StatusCommandHandler())
        self.command_manager.register("users", ListUsersCommandHandler(self.ws_manager))
        self.command_manager.register("msg", MessageCommandHandler(self.ws_manager))

        self.command_manager.register("load_character", LoadCharacterCommandHandler(self))
        self.command_manager.register("agents", ListAgentsCommandHandler(self))

        for yaml_path in settings.COMMANDS_YAML_PATH:
            commands = CommandLoader.load_commands(yaml_path)
            for cmd_name, cmd_info in commands.items():
                self.command_manager.register(cmd_name, cmd_info['handler'])

    async def load_characters(self):
        logger.info("Loading characters")
        for filepath in settings.CHARACTERS_PATH:
            await self.character_manager.load_character(filepath)




    async def startup(self,app:FastAPI):
        if self._initialized:
            return
        logger.info(f"Worker {self.worker_id} starting up...")
        try:
            self.app = app
            await self.redis_manager.init_pool()
            await self.memory_manager.init_pool()
            await self.event_handler.start()
            setup_websocket(self.app, self)
            await self.load_characters()
            self.load_commands()

            asyncio.create_task(self._health_check())
            self._initialized = True

        except Exception as e:
            logger.error(f"Worker {self.worker_id} Error during startup: {e}")
            await self.shutdown()
            raise

    async def shutdown(self):
        logger.info(f"Worker {self.worker_id} Application begins to shutdown...")

        try:
            if self.event_handler:
                await self.event_handler.stop()
        except Exception as e:
            logger.error(f"Error stopping event handler: {e}")

        try:
            if self.memory_manager:
                await self.memory_manager.close()
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")

        try:
            if self.redis_manager:
                await self.redis_manager.close()
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")

        logger.info(f"Worker {self.worker_id} Application shutdown complete")


    async def _health_check(self):
        while True:
            try:
                await self.redis_manager.ping()
                await self.memory_manager.ping()

                await self.redis_manager.hset(
                    "worker_status",
                    self.worker_id,
                    json.dumps({
                        "last_check": time.time(),
                        "uptime": time.time() - self.start_time,
                        "connections": {
                            "db": self.memory_manager.size(),
                            "redis": self.redis_manager.size()
                        }
                    })
                )
            except Exception as e:
                logger.error(f"Health check failed: {e}")

            await asyncio.sleep(self._health_check_interval)


    async def get_status(self) -> dict:
        return {
            "worker_id": self.worker_id,
            "uptime": time.time() - self.start_time,
            "connections": {
                "redis": self.redis_manager.size()
            }
        }
    def add_router(self, router: APIRouter):
        self.app.include_router(router)
        logger.info(f"Worker {self.worker_id} include_router")


runtime = RuntimeState()
