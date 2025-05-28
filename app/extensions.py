import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
load_dotenv()

from app.config.settings import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class AsyncDatabase:
    def __init__(self):
        self._engine = None
        self.async_session = None

    def init(self) -> None:
        self._engine = create_async_engine(
            url=settings.ASYNC_DATABASE_URI,
            echo=os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true",
            pool_size=int(os.getenv("SQLALCHEMY_POOL_SIZE", 20)),
            max_overflow=int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", 10)),
            pool_pre_ping=os.getenv("SQLALCHEMY_POOL_PRE_PING", "true").lower() == "true",
        )
        self.async_session = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.async_session() as session:
            yield session

    # @asynccontextmanager
    # def get_async_session(self) -> async_sessionmaker[AsyncSession]:
    #     return self.async_session()

    @property
    def engine(self):
        if not self._engine:
            raise RuntimeError("Async engine não inicializada. Chame init_app primeiro.")
        return self._engine


async_db = AsyncDatabase()
