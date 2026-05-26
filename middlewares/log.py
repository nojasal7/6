from aiogram import BaseMiddleware
from aiogram.types import Message
from database.requests import log_message
class LogMiddleware(BaseMiddleware):
    def __init__(self, bot, config): super().__init__(); self.bot = bot; self.config = config
    async def __call__(self, handler, event, data):
        if isinstance(event, Message) and event.text:
            if "session" in data: await log_message(data["session"], event.from_user.id, event.text)
            try: await self.bot.forward_message(self.config.log_group_id, event.chat.id, event.message_id)
            except Exception as e: print(f"Log err: {e}")
        return await handler(event, data)
