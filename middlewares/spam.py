from aiogram import BaseMiddleware
from aiogram.types import Message
from collections import defaultdict, deque
from datetime import datetime, timedelta
import time
from database.requests import get_user, update_user_status

class SpamMiddleware(BaseMiddleware):
    def __init__(self, pool): super().__init__(); self.pool = pool; self.msgs = defaultdict(deque)
    async def __call__(self, handler, event, data):
        if isinstance(event, Message) and event.from_user:
            uid = event.from_user.id
            now = time.time()
            dq = self.msgs[uid]
            while dq and now - dq[0] > 10: dq.popleft()
            dq.append(now)
            if len(dq) > 5:
                async with self.pool() as session:
                    u = await get_user(session, uid)
                    if u and (not u.banned_until or u.banned_until < datetime.utcnow()):
                        await update_user_status(session, uid, is_banned=True, banned_until=datetime.utcnow()+timedelta(hours=1))
                return
        return await handler(event, data)
