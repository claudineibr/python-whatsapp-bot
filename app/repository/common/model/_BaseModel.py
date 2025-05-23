from datetime import datetime

from sqlalchemy import (
    DateTime,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.extensions import db


class BaseModel(db.Model):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=False)
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
