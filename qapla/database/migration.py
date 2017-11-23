from alembic import command
from alembic.config import Config
from sqlalchemy.orm import sessionmaker

__all__ = ['recreate_database']


def recreate_database(database, path_to_migrations):
    """
    Drop old database and migrate from scratch.
    """
    _clear_database(database)
    _migrate(path_to_migrations)


def _clear_database(database):
    """
    In order to drop database, we need to connect to another one (using
    default_url). With that connection we need to drop and create new
    database.
    """
    dbname = database.get_dbname()
    engine = database.get_engine(True)
    session = sessionmaker(bind=engine)()
    session.connection().connection.set_isolation_level(0)
    session.execute('DROP DATABASE IF EXISTS {}'.format(dbname))
    session.execute('CREATE DATABASE {}'.format(dbname))
    session.close()


def _migrate(path_to_migrations):
    alembic_cfg = Config()
    alembic_cfg.set_main_option('script_location', path_to_migrations)
    alembic_cfg.set_main_option('is_test', 'true')
    command.upgrade(alembic_cfg, "head")
