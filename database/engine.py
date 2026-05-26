from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from .models import Base

def get_engine(url: str):
    return create_async_engine(
        url,
        pool_pre_ping=True,              # Проверка соединения перед использованием
        pool_recycle=3600,               # Пересоздавать соединения раз в час
        echo=False                       # Логирование SQL запросов (поставьте True для отладки)
    )

def get_sessionmaker(eng):
    return async_sessionmaker(eng, expire_on_commit=False)

async def create_db(eng):
    async with eng.begin() as conn:
        # MySQL требует, чтобы таблицы были InnoDB для поддержки транзакций
        await conn.run_sync(Base.metadata.create_all)
