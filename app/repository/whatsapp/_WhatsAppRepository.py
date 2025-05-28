import json
from functools import cache

from sqlalchemy import select, text
from app.model import WhatsAppChatMessage
from app.schemas import WhatsAppChatMessageCreate, WhatsAppChatMessageUpdate
from app.extensions import async_db


@cache
class WhatsAppRepository:

    @staticmethod
    async def test_connection():
        async with async_db.get_async_session() as session:
            result = await session.execute(text('SELECT 1'))
            value = result.scalar()
            return {'status': 'success', 'data': value == 1}

    @staticmethod
    async def find_messages():
        async with async_db.get_async_session() as session:
            result = await session.execute(select(WhatsAppChatMessage))
            users = result.scalars().all()
            return json.dumps([{"id": u.id, "name": u.name} for u in users])

    @staticmethod
    async def create_message(message: WhatsAppChatMessageCreate):
        async with async_db.get_async_session() as session:
            message = WhatsAppChatMessage(**message.model_dump())
            session.add(message)
            await session.commit()
            await session.refresh(message)
            return message

    @staticmethod
    async def update_status_message(data: WhatsAppChatMessageUpdate):
        async with async_db.get_async_session() as session:
            message = await session.get(WhatsAppChatMessage, data.message_id)
            if not message:
                return None

            if not hasattr(message, data.status):
                return
            try:
                setattr(message, data.status, data.mark_as)
                await session.commit()
                await session.refresh(message)
                return message
            except:
                session.rollback()
                raise
