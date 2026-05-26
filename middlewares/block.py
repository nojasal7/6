from aiogram import BaseMiddleware
from aiogram.types import Message
from database.requests import get_user, add_user, update_user_status
from datetime import datetime


class BlockMiddleware(BaseMiddleware):
    def __init__(self, config):
        super().__init__()
        self.config = config

    async def __call__(self, handler, event, data):
        uid = event.from_user.id if hasattr(event, "from_user") else None

        if uid:
            # Always allow admin
            if uid == self.config.admin_id:
                return await handler(event, data)

            # ✅ CRITICAL FIX: Always allow /start so new users can register
            if isinstance(event, Message) and event.text and event.text.startswith("/start"):
                return await handler(event, data)

            session = data["session"]
            user = await get_user(session, uid)

            # If user doesn't exist and isn't sending /start, block them
            if not user:
                if isinstance(event, Message):
                    await event.answer("⚠️ Please press /start first.")
                return

            # Check temporary spam ban
            if user.is_banned:
                if user.banned_until and user.banned_until < datetime.utcnow():
                    await update_user_status(session, uid, is_banned=False, banned_until=None)
                else:
                    if isinstance(event, Message):
                        await event.answer("🚫 You are banned.")
                    return

            # Check approval status
            if not user.is_approved:
                if isinstance(event, Message):
                    await event.answer("⏳ You are not approved to use this bot yet.")
                return

        return await handler(event, data)
