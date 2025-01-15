import asyncio
from typing import Callable, Dict, Any

from redis import RedisError

from argo.configs import logger
from argo.kernel.schema import EventMessage


class EventHandler:
    def __init__(self,redis_manager):
        self._redis_manager = redis_manager
        self._pubsub = None
        self._task = None
        self._running = False
        self._redis = None
        self._handlers: Dict[str, Callable] = {}

    async def start(self):
        self._running = True
        try:
            async with self._redis_manager.get_connection() as redis:
                self._redis = redis
                self._pubsub = redis.pubsub()
                await self._pubsub.subscribe("event_bus")
                self._task = asyncio.create_task(self._handle_messages(self._pubsub))
                logger.info("Event handler started")
        except Exception as e:
            logger.error(f"Failed to start event handler: {e}")
            self._running = False
            raise

    async def stop(self):
        logger.info("Stopping event handler...")
        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"Error cancelling task: {e}")
            self._task = None

        if self._pubsub:
            try:
                await self._pubsub.unsubscribe()
                await self._pubsub.close()
            except RedisError as e:
                logger.warning(f"Failed to close Redis pubsub connection: {e}")
            except Exception as e:
                logger.error(f"Unexpected error closing pubsub: {e}")
            finally:
                self._pubsub = None

        logger.info("Event handler stopped")

    async def _handle_messages(self, pubsub):
        try:
            while self._running:
                try:
                    async for message in pubsub.listen():
                        if not self._running:
                            break

                        if message["type"] == "message":
                            await self._process_message(message)
                except RedisError as e:
                    if not self._running:
                        logger.debug(f"Redis connection closed during shutdown: {e}")
                    else:
                        logger.error(f"Redis error while processing message: {e}")
                    break
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    if self._running:
                        await asyncio.sleep(1)
                    else:
                        break
        except Exception as e:
            logger.error(f"Fatal error in message handling: {e}")
        finally:
            logger.debug("Message handling loop ended")


    async def _process_message(self, message):
        try:
            event_message = EventMessage.from_json(message["data"])
            handler = self._handlers.get(event_message.evt)

            if handler:
                await handler(event_message.data)
            else:
                logger.warning(f"No handler found for event: {event_message.evt}")

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def add_handler(self, event_type: str, handler: Callable):
        self._handlers[event_type] = handler
        logger.info(f"Added handler for event type: {event_type}")

    async def publish_event(self, evt: str, data: Any):
        message = EventMessage(evt=evt, data=data)
        try:
            await self._redis.publish("event_bus", message.to_json())
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            raise