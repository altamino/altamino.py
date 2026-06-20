from __future__ import annotations
from altamino.objects.resp import Event
from typing import Callable

from altamino.ws.router import Router

class AsyncRouter(Router):


    @staticmethod
    def command_validator(commands: list[str], handler: Callable):
        async def wrapped_handler(data: Event):
            if not isinstance(data.message.content, str):
                return
            message_content = data.message.content.lower()
            for command in commands:
                if message_content.startswith(command.lower()):
                    data.message.content = data.message.content[len(command):].strip()
                    await handler(data)
                    break
        return wrapped_handler


    def __init__(self):
        super().__init__()