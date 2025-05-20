import asyncio

from alembic import context

from app.extensions import db


def include_object(object, name, type_, reflected, compare_to):
    # Filtra objetos por schema
    if hasattr(object, 'schema'):
        if object.schema == 'public':
            return False  # Ignora o schema public
    return True


def run_migrations_online():
    connectable = db.engine

    def do_run_migrations(connection):
        context.configure(
            connection=connection,
            target_metadata=db.metadata,
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
