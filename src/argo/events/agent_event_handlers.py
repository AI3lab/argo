import time

from argo.configs import logger


class AgentEventHandlers:
    @staticmethod
    async def handle_user_changed(data: dict):
        agent_id = data.get("agent_id")
        changes = data.get("changes")
        logger.info(f"agent {agent_id} changed: {changes}")

    @staticmethod
    async def handle_user_login(data: dict):
        user_id = data.get("user_id")
        login_time = data.get("login_time")
        logger.info(f"agent {user_id} logged in at {login_time}")

"""
Example:

async def user_login(user_id: int):

    await runtime_state.event_handler.publish_event(
        "user_login",
        {
            "user_id": user_id,
            "login_time": time.time(),
            "ip": "192.168.1.1"
        }
    )

"""
