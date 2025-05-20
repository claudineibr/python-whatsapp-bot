import asyncio

from flask import app

from extensions import db


async def test_database_connection():
    async with app.app_context():
        async with db.engine.connect() as conn:
            result = await conn.execute("SELECT 1")
            print(await result.scalar())

asyncio.run(test_database_connection())
