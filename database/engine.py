from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from .models import Base

def get_engine(url: str):
    return create_async_engine(url)

def get_sessionmaker(eng):
    return async_sessionmaker(eng, expire_on_commit=False)

async def create_db(eng):
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
