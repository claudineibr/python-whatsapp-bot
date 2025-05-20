from repository.common.model import BaseModel
from app.extensions import db
from sqlalchemy import Uuid

class WhatsAppChatMessage(BaseModel):

    __tablename__ = 'whatsapp_chat_messages'
    __table_args__ = {'schema': 'whatsapp_chat'}

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    code = db.Column(Uuid, unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    message = db.Column(db.String(5000), nullable=False)

