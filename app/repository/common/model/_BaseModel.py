from datetime import datetime

from sqlalchemy import (
    DateTime,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    DeclarativeBase,
    mapped_column,
)

class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
