from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base


engine = create_async_engine('postgresql+asyncpg://postgres:qwerty@localhost:5432/restaurant')

Base = declarative_base()

async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session