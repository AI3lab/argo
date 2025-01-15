from typing import Dict, List

from argo.command.commands import CommandHandler, CommandContext
from argo.configs import logger


class CommandManager:
    def __init__(self):
        self._commands: Dict[str, CommandHandler] = {}

    def register(self, command: str, handler: CommandHandler):
        self._commands[command.lower()] = handler
        logger.info(f"Registered {command} handler {handler}")

    def unregister(self, command: str):
        self._commands.pop(command.lower(), None)

    async def execute(self, command: str, args: List[str], context: CommandContext):

        handler = self._commands.get(command.lower())
        if handler:
            try:
                await handler.execute(args, context)
            except Exception as e:
                await context.ws.send_text(f"Error executing command {command}: {str(e)}")
        else:
            await context.ws.send_text(f"Unknown command: {command}")

    def get_help(self) -> str:
        help_text = "Available command:\n"
        for cmd, handler in sorted(self._commands.items()):
            help_text += f"/{cmd} - {handler.description}\n"
        return help_text

    def get_command_handler(self, command: str) -> CommandHandler:

        return self._commands.get(command.lower())

    def has_command(self, command: str) -> bool:

        return command.lower() in self._commands

    def get_commands(self) -> List[str]:
        return sorted(self._commands.keys())