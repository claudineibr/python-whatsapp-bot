from sqlalchemy import (
    Column,
    String,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData

metadata = MetaData(schema="common")
Base = declarative_base(metadata=metadata)

class VersionTable(Base):

    __tablename__ = 'alembic_version'
    version_num = Column(String(32), primary_key=True)
