import logging

from sqlalchemy import (
    create_engine,
    text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self, db_name: str) -> None:

        self.db_name = db_name
        engine = self.__get_engine()
        Base.metadata.create_all(engine)
        self.db_session = sessionmaker(bind=engine)

    def test_connection(self):
        with self.db_session() as session:
            session.execute(text('SELECT 1'))
            logger.debug(f"Connection successful to database: {self.db_name}")

    def __get_engine(self):
        try:
            return create_engine(f"postgresql+psycopg2://root:root@host.docker.internal:5433/{self.db_name}")
        except Exception as e:
            logger.exception(f"Error load connection to database: {self.db_name}")
            raise e
