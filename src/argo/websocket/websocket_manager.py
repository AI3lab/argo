from typing import Dict, List
from fastapi import WebSocket

from argo.configs import logger


class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, uid: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[uid] = websocket
        await self.broadcast(f"User {uid} connected")
        logger.info(f"Accepted new connection:{websocket.client.host}:{websocket.client.port}")

    def disconnect(self, uid: str):
        if uid in self.active_connections:
            del self.active_connections[uid]

    async def broadcast(self, message: str):
        disconnected_uids = []
        for uid, connection in self.active_connections.items():
            try:
                await connection.send_text(message)
            except RuntimeError as e:
                logger.error(f"Failed to broadcast message to {uid}: {e}")
                disconnected_uids.append(uid)

        for uid in disconnected_uids:
            self.disconnect(uid)

    async def send_to_user(self, uid: str, message: str):
        if uid in self.active_connections:
            try:
                if isinstance(message, str):
                    await self.active_connections[uid].send_text(message)
                elif isinstance(message, dict):
                    await self.active_connections[uid].send_json(message)
                return True
            except RuntimeError as e:
                logger.error(f"Failed sending message to user{uid}: {e}")
                self.disconnect(uid)
            except Exception as e:
                logger.error(f"Error sending message to user {uid}: {e}")
                self.disconnect(uid)
                return False
        else:
            logger.error(f"No active connection for {uid}")
        return False


