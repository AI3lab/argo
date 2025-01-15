from typing import List

from starlette.websockets import WebSocket

from argo.websocket.websocket_manager import WebSocketManager


class CommandContext:
    def __init__(self, uid: str, ws: WebSocket, runtime_state):
        self.uid = uid
        self.ws = ws
        self.runtime_state = runtime_state

class CommandHandler:
    def __init__(self, description: str):
        self.description = description


    async def execute(self, args: List[str], context: CommandContext) -> None:
        raise NotImplementedError

class HelpCommandHandler(CommandHandler):
    def __init__(self, command_manager):
        super().__init__("Show help information")
        self._manager = command_manager

    async def execute(self, args: List[str], context: CommandContext):
        await context.ws.send_text(self._manager.get_help())

class StatusCommandHandler(CommandHandler):
    def __init__(self):
        super().__init__("Show current system status")

    async def execute(self, args: List[str], context: CommandContext):
        status = await context.runtime_state.get_status()
        await context.ws.send_text(f"System Status:\n{status}")

class ListUsersCommandHandler(CommandHandler):
    def __init__(self, ws_manager: WebSocketManager):
        super().__init__("List all connected users")
        self._ws_manager = ws_manager

    async def execute(self, args: List[str], context: CommandContext):
        users = list(self._ws_manager.active_connections.keys())
        await context.ws.send_text(f"Connected users: {', '.join(users)}")

class ListAgentsCommandHandler(CommandHandler):
    def __init__(self, command_manager):
        super().__init__("List all connected agents")
        self._manager = command_manager

    async def execute(self, args: List[str], context: CommandContext):
        agents = await context.runtime_state.character_manager.list_characters()
        print(agents)
        await context.ws.send_text(f"Connected agents: {', '.join(agents)}")




class LoadCharacterCommandHandler(CommandHandler):
    def __init__(self, command_manager):
        super().__init__("Load character")
        self._manager = command_manager

    async def execute(self, args: List[str], context: CommandContext):
        filepath = args.pop(0)
        success,character,error = await context.runtime_state.character_manager.load_character(filepath)
        if not success:
            await context.ws.send_text(error)
        else:
            await context.ws.send_text(f"Load {character.name} character successfully")


class MessageCommandHandler(CommandHandler):
    def __init__(self, ws_manager: WebSocketManager):
        super().__init__("Send private message to user: /msg user_id message")
        self._ws_manager = ws_manager

    async def execute(self, args: List[str], context: CommandContext):
        if len(args) < 2:
            await context.ws.send_text("Usage: /msg user_id message")
            return

        target_uid = args[0]
        message = ' '.join(args[1:])

        if await self._ws_manager.send_to_user(target_uid,
                                               f"Private message from {context.uid}: {message}"):
            await context.ws.send_text(f"Message sent to {target_uid}")
        else:
            await context.ws.send_text(f"User {target_uid} is not connected")

