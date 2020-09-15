from alembic import context


def run_migrations(dbplugin, metadata):
    if context.is_offline_mode():
        run_migrations_offline(dbplugin, metadata)
    else:
        run_migrations_online(dbplugin, metadata)


def run_migrations_offline(dbplugin, metadata):
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=dbplugin.url,
        target_metadata=metadata,
        literal_binds=True,
    )

    run_alembic_migrations()


def run_migrations_online(dbplugin, metadata):
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = dbplugin.create_engine()

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=metadata)

        run_alembic_migrations()


def run_alembic_migrations():
    with context.begin_transaction():
        context.run_migrations()
