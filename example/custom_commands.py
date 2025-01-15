from argo.command.commands import CommandHandler, CommandContext

class MyCustomCommand(CommandHandler):
    def __init__(self, description: str, **kwargs):
        super().__init__(description)

    async def execute(self, args: list, context: CommandContext):
        await context.ws.send_text(f"Executing custom command with args: {args}")