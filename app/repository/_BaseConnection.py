import logging
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.extensions import async_db

logger = logging.getLogger(__name__)


class DatabaseConnection:

    @classmethod
    async def test_connection(cls) -> bool:
        async with async_db.get_async_session() as session:
            result = await session.execute(text('SELECT 1'))
            value = result.scalar()
            return value == 1

    @classmethod
    async def get_async_session(cls) -> AsyncGenerator[AsyncSession, None]:
        async with async_db.get_async_session() as session:
            yield session
