from pydantic import BaseModel


class WhatsAppChatMessageCreate(BaseModel):
    name: str
    phone: str
    message_type: str
    message_id: str
    message: str


class WhatsAppChatMessageUpdate(BaseModel):
    message_id: str
    status: str
    mark_as: bool
