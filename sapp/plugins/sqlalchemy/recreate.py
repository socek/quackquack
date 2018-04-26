from alembic import command
from alembic.config import Config
from sqlalchemy.orm import sessionmaker


class RecreateDatabases(object):
    def __init__(self, configurator):
        self.configurator = configurator
        self.dbplugins = configurator.dbplugins
        self.databases = []

    def append_database(self, name, path_to_migrations):
        self.databases.append((name, path_to_migrations))

    def make(self):
        for name, path_to_migrations in self.databases:
            self._clear_database(self.get_db(name))
            self._migrate(path_to_migrations)

    def _clear_database(self, database):
        """
        In order to drop database, we need to connect to another one (using
        default_url). With that connection we need to drop and create new
        database.
        """
        dbname = database.get_dbname()
        engine = database.get_engine(default_url=True)
        session = sessionmaker(bind=engine)()
        session.connection().connection.set_isolation_level(0)
        session.execute('DROP DATABASE IF EXISTS {}'.format(dbname))
        session.execute('CREATE DATABASE {}'.format(dbname))
        session.close()

    def _migrate(self, path_to_migrations):
        alembic_cfg = Config()
        alembic_cfg.set_main_option('script_location', path_to_migrations)
        alembic_cfg.set_main_option('is_test', 'true')
        command.upgrade(alembic_cfg, "head")

    def get_db(self, name):
        return self.configurator.dbplugins[name]
