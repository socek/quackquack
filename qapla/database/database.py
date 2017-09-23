from alembic import command
from alembic.config import Config
from sqlalchemy.engine import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import sessionmaker

from qapla.database.exceptions import SettingMissing
from qapla.database.request import RequestDBSessionGenerator


class Database(object):
    _PREFIX = 'db'

    def __init__(self, name='database'):
        self.name = name

    def add_to_app(self, app):
        self.app = app
        self.settings = app.settings
        self._validate_settings()
        self.engine = self.get_engine()
        self.sessionmaker = sessionmaker(bind=self.engine)

    def add_to_web(self):
        self.app.config.registry[self.name] = self.sessionmaker
        self.app.config.add_request_method(
            RequestDBSessionGenerator(self.name),
            name=self.name,
            reify=True)

    def recreate(self):
        """
        Drop old database and migrate from scratch.
        """
        self._drop_database()
        self._migrate()

    def _drop_database(self):
        dbname = self.get_dbname()
        engine = self.get_engine(True)
        session = sessionmaker(bind=engine)()
        session.connection().connection.set_isolation_level(0)
        session.execute('DROP DATABASE {}'.format(dbname))
        session.execute('CREATE DATABASE {}'.format(dbname))
        session.close()

    def _migrate(self):
        alembic_cfg = Config()
        alembic_cfg.set_main_option('script_location', 'versions')  # TODO: change this to a path from settings
        alembic_cfg.set_main_option('db_app_name', self.name)
        command.upgrade(alembic_cfg, "head")

    def _validate_settings(self):
        to_validate = ['url', 'default_url']
        for subkey in to_validate:
            self._validate_setting_exists(subkey)
            make_url(self.get_setting(subkey))

    def _validate_setting_exists(self, subkey):
        key = self._get_key(subkey)
        if key not in self.settings:
            raise SettingMissing(
                key,
                "'{0}' key is needed for use '{1}'' database in application".format(
                    key,
                    self.name))

    def _get_key(self, subkey=None):
        keys = [self._PREFIX, self.name]
        if subkey:
            keys.append(subkey)
        return ':'.join(keys)

    def get_setting(self, subkey, default=NotImplemented):
        key = self._get_key(subkey)
        if default is NotImplemented:
            return self.settings[key]
        else:
            return self.settings.get(key, default)

    def get_engine(self, default_url=False):
        url = self.get_url(default_url)
        return create_engine(
            url,
            **self.get_setting('options', {}))

    def get_url(self, default_url=False):
        """
        Get url from settings.
        """
        subkey = 'default_url' if default_url else 'url'
        return self.get_setting(subkey)

    def get_dbname(self):
        """
        Get database name.
        """
        return make_url(self.get_url()).database

    def get_session(self):
        return self.sessionmaker()
