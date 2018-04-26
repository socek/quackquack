from alembic import context


class AlembicScript(object):
    def __init__(self, app, base_model, dbname):
        self.app = app
        self.base_model = base_model
        self.metadata = self.base_model.metadata
        self.dbname = dbname

    def run(self):
        self._init_app()
        self.dbplugin = self._get_dbplugin()
        self._run_migration_depending_on_offline_mode()

    def _get_dbplugin(self):
        return self.app.dbplugins[self.dbname]

    def _init_app(self):
        startpoint = 'tests' if context.config.get_main_option(
            'is_test', False) else 'command'
        self.app.start(startpoint)

    def _run_migration_depending_on_offline_mode(self):
        if context.is_offline_mode():
            self.run_migrations_offline()
        else:
            self.run_migrations_online()

    def run_migrations_offline(self):
        """Run migrations in 'offline' mode.

        This configures the context with just a URL
        and not an Engine, though an Engine is acceptable
        here as well.  By skipping the Engine creation
        we don't even need a DBAPI to be available.

        Calls to context.execute() here emit the given string to the
        script output.

        """
        url = self.dbplugin.get_url()

        context.configure(
            url=url, target_metadata=self.metadata, literal_binds=True)

        self.run_migrations()

    def run_migrations_online(self):
        """Run migrations in 'online' mode.

        In this scenario we need to create an Engine
        and associate a connection with the context.

        """
        connectable = self.dbplugin.get_engine()

        with connectable.connect() as connection:
            context.configure(
                connection=connection, target_metadata=self.metadata)

            self.run_migrations()

    def run_migrations(self):
        with context.begin_transaction():
            context.run_migrations()
