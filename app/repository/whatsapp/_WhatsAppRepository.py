import json
from functools import cache

from model import WhatsAppChatMessage
from schemas import WhatsAppChatMessageCreate
from .._BaseConnection import DatabaseConnection
from sqlalchemy import select


@cache
class WhatsAppRepository(DatabaseConnection):

    async def test_connection(self):
        result = await super().test_connection()
        return {'status': 'success', 'data': result}

    async def find_messages(self):
        async with self.get_async_session() as session:
            result = await session.execute(select(WhatsAppChatMessage))
            users = result.scalars().all()
            return json.dumps([{"id": u.id, "name": u.name} for u in users])

    async def create_message(self, message: WhatsAppChatMessageCreate):
        async with self.get_async_session() as session:
            message = WhatsAppChatMessage(**message.model_dump())
            session.add(message)
            await session.commit()
            await session.refresh(message)
            return message
