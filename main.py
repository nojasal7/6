import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import load_config
from database.engine import get_engine, get_sessionmaker, create_db

from middlewares.db import DbSessionMiddleware
from middlewares.text_only import TextOnlyMiddleware
from middlewares.log import LogMiddleware
from middlewares.spam import SpamMiddleware
from middlewares.block import BlockMiddleware

from handlers import admin, user, group

async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    config = load_config(".env")
    
    bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    
    engine = get_engine(config.db_url)
    await create_db(engine)
    session_pool = get_sessionmaker(engine)
    
    dp["config"] = config
    
    # Middleware order is crucial
    dp.update.outer_middleware(DbSessionMiddleware(session_pool))
    dp.update.outer_middleware(TextOnlyMiddleware())
    dp.update.outer_middleware(LogMiddleware(bot, config))
    dp.update.outer_middleware(SpamMiddleware(session_pool))
    dp.update.outer_middleware(BlockMiddleware(config))
    
    dp.include_router(admin.router)
    dp.include_router(user.router)
    dp.include_router(group.router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped")
    
