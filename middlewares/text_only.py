from aiogram import BaseMiddleware
from aiogram.types import Message
class TextOnlyMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, Message) and not event.text: return
        return await handler(event, data)
