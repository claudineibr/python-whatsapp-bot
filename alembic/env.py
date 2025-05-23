import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from external import FlaskMessageHandler

from alembic import context
from app.extensions import db, async_db

flask_message_handler = FlaskMessageHandler()
flask_message_handler.create_app()

config = context.config
target_metadata = db.metadata

def include_object(object, name, type_, reflected, compare_to):
    return not getattr(object, 'schema', None) == 'public'


def run_migrations_online():
    connectable = async_db.engine
    def do_run_migrations(connection):
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_schemas=True,
            include_object=include_object,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()

    async def run_async_migrations():
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)

    asyncio.run(run_async_migrations())

run_migrations_online()
