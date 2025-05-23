from uuid import uuid4, UUID
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from repository.common.model import BaseModel

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column


class WhatsAppChatMessage(BaseModel):
    __tablename__ = 'whatsapp_chat_messages'
    __table_args__ = {'schema': 'whatsapp_chat'}

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    code: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), default=uuid4, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    message_type: Mapped[str] = mapped_column(String(15), nullable=False)
    message_id: Mapped[str] = mapped_column(String(300), nullable=False)
    message: Mapped[str] = mapped_column(String(8000), nullable=False)
    sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    delivered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
