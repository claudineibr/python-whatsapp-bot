from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class WhatsAppChatMessageCreate(BaseModel):
    name: str
    phone: str
    message_type: str
    message_id: str
    message: str


class WhatsAppChatMessageRead(WhatsAppChatMessageCreate):
    id: int
    code: UUID
    sent: bool
    delivered: bool
    read: bool
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        orm_mode = True
