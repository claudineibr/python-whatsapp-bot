from contextlib import asynccontextmanager
from typing import AsyncGenerator

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


class AsyncDatabase:
    def __init__(self):
        self._engine = None
        self._session = None

    def init_app(self, app: Flask) -> None:
        self._engine = create_async_engine(
            url=app.config["ASYNC_SQLALCHEMY_DATABASE_URI"],
            echo=app.config.get("SQLALCHEMY_ECHO", False),
            pool_size=app.config.get("SQLALCHEMY_POOL_SIZE", 20),
            max_overflow=app.config.get("SQLALCHEMY_MAX_OVERFLOW", 10),
            pool_pre_ping=app.config.get("SQLALCHEMY_POOL_PRE_PING", True)
        )
        self._session = sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    @asynccontextmanager
    async def get_async_session(self)-> AsyncGenerator[AsyncSession, None]:
        async with self._session() as session:
            yield session

    @property
    def engine(self):
        if not self._engine:
            raise RuntimeError("Async engine não inicializada. Chame init_app primeiro.")
        return self._engine


db = SQLAlchemy()
migrate = Migrate()
async_db = AsyncDatabase()
