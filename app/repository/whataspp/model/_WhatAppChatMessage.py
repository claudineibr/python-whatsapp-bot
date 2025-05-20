from app.common.model import BaseModel
from app.extensions import db


class WhatAppChatMessage(BaseModel):

    __tablename__ = 'WhatAppChatMessage'
    __table_args__ = {'schema': 'WhatsappChat'}

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    message = db.Column(db.String(5000), nullable=False)

