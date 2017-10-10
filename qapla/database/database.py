from alembic import command
from alembic.config import Config
from sqlalchemy.engine import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from qapla.database.exceptions import SettingMissing
from qapla.database.request import RequestDBSessionGenerator


class ConfigurationError(Exception):

    def __init__(self, description):
        super().__init__()
        self.description = description


class DatabaseSetting(object):
    """
    Settings for the database.
    This class will help set settings for the database. Making settings key may
    be a little bit difficult, that is why this class is design for.

    Expected values:
    - url* - url for the sqlalchemy database
    - default_url* - url for different sqlalchemy database which allows dropping
        and creating the first one
    - options - arguments which will be passed to the sqlalchemy's create_engine

    * - mandatory arguments, which wll be validated and raise an error if don't.
    """
    _PREFIX = 'db'
    _SETTING_MISSING_FORMAT = (
        "'{0}' key is needed for use '{1}'' database in application")
    _TO_VALIDATE = ('url', 'default_url')

    def __init__(self, settings, name='database'):
        self.name = name
        self.settings = settings

    def get_key(self, subkey=None):
        keys = [self._PREFIX, self.name]
        if subkey:
            keys.append(subkey)
        return ':'.join(keys)

    def __getitem__(self, subkey):
        key = self.get_key(subkey)
        return self.settings[key]

    def __setitem__(self, subkey, value):
        key = self.get_key(subkey)
        self.settings[key] = value

    def get(self, subkey, default=None):
        key = self.get_key(subkey)
        return self.settings.get(key, default)

    def validate(self):
        for subkey in self._TO_VALIDATE:
            self.validate_exists(subkey)
            make_url(self[subkey])

    def validate_exists(self, subkey):
        key = self.get_key(subkey)
        if key not in self.settings:
            raise SettingMissing(
                key,
                self._SETTING_MISSING_FORMAT.format(key, self.name))


class Database(object):

    def __init__(self, name='database', paths_key='migrations'):
        self.name = name
        self.paths_key = paths_key
        self.app = None

    def add_to_app(self, app):
        self.app = app
        self.settings = DatabaseSetting(app.settings, self.name)
        self.settings.validate()
        self.paths = app.paths
        self.engine = self.get_engine()
        self._create_session_maker()

    def _create_session_maker(self):
        self.sessionmaker = scoped_session(sessionmaker(bind=self.engine))

    def add_to_web(self):
        if not self.app:
            raise ConfigurationError('.add_to_web should be called AFTER .add_to_app')
        self.app.config.registry[self.name] = self.sessionmaker
        self.app.config.add_request_method(
            RequestDBSessionGenerator(self.name),
            name=self.name,
            reify=True)

    def recreate(self):
        """
        Drop old database and migrate from scratch.
        """
        self._clear_database()
        self._migrate()

    def _clear_database(self):
        """
        In order to drop database, we need to connect to another one (using
        default_url). With that connection we need to drop and create new
        database.
        """
        dbname = self.get_dbname()
        engine = self.get_engine(True)
        session = sessionmaker(bind=engine)()
        session.connection().connection.set_isolation_level(0)
        session.execute('DROP DATABASE IF EXISTS {}'.format(dbname))
        session.execute('CREATE DATABASE {}'.format(dbname))
        session.close()

    def _migrate(self):
        alembic_cfg = Config()
        alembic_cfg.set_main_option(
            'script_location',
            self.paths.get(self.paths_key))
        alembic_cfg.set_main_option('is_test', 'true')
        command.upgrade(alembic_cfg, "head")

    def get_engine(self, default_url=False):
        url = self.get_url(default_url)
        return create_engine(
            url,
            **self.settings.get('options', {}))

    def get_url(self, default_url=False):
        """
        Get url from settings.
        """
        subkey = 'default_url' if default_url else 'url'
        return self.settings[subkey]

    def get_dbname(self):
        """
        Get database name.
        """
        return make_url(self.get_url()).database

    def get_session(self):
        return self.sessionmaker()

    def close(self):
        self.sessionmaker.remove()
