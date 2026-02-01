
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine , AsyncSession
from app.core.config import get_settings 
from typing import AsyncGenerator 


settings = get_settings()
DATABASE_URL = settings.DATABASE_URL

# We create an asynchronous engine for working with a database
engine = create_async_engine(DATABASE_URL , echo=True)
# Create a session factory to interact with the database
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)



# Dependency to use in FastAPI routes
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
