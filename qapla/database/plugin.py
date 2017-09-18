from alembic import command
from alembic.config import Config
from sqlalchemy.engine import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import sessionmaker

from qapla.database.exceptions import SettingMissing
from qapla.database.request import RequestDBSessionGenerator


class DatabasePlugin(object):
    DB_KEY = 'db:url'
    TEST_DB_KEY = 'db:test_url'
    DEFAULT_DB_KEY = 'db:default_url'

    _DATABASES = (
        None,
        DB_KEY,
        TEST_DB_KEY,
        DEFAULT_DB_KEY)

    def __init__(self, app):
        self.app = app
        self.settings = app.settings
        self.paths = app.paths

    def add_to_app(self):
        self.validate_settings()
        self.engine = self.get_engine()
        self.sessionmaker = sessionmaker(bind=self.engine)

    def add_to_web(self):
        self.app.config.registry.sessionmaker = self.sessionmaker
        self.app.config.add_request_method(
            RequestDBSessionGenerator(),
            name='database',
            reify=True)

    def validate_settings(self):
        """
        Raise error if settings is not fully configured.
        """
        if self.DB_KEY not in self.settings:
            raise SettingMissing(
                self.DB_KEY,
                "'{}' key is needed for use database in server application")

        if self.TEST_DB_KEY not in self.settings:
            raise SettingMissing(
                self.DB_KEY,
                "'{}' key is needed for use database in tests")

        if self.DEFAULT_DB_KEY not in self.settings:
            raise SettingMissing(
                self.DB_KEY,
                "'{}' key is needed for so we can recreate database")

        # validate format
        make_url(self.settings[self.DB_KEY])
        make_url(self.settings[self.TEST_DB_KEY])
        make_url(self.settings[self.DEFAULT_DB_KEY])

    def get_engine(self, dbkey=None):
        url = self.get_url(dbkey)
        return create_engine(url, **self.settings['db:options'])

    def get_url(self, dbkey=None):
        """
        Get url from settings. If not setting's key provided, then choose one
        depending on the is_test setting.
        """
        assert dbkey in self._DATABASES

        if not dbkey:
            is_test = self.settings.get('is_test', False)
            dbkey = self.TEST_DB_KEY if is_test else self.DB_KEY

        return self.settings[dbkey]

    def recreate(self):
        """
        Drop old database and migrate from scratch.
        """
        dbname = make_url(self.get_url()).database

        engine = self.get_engine(self.DEFAULT_DB_KEY)
        session = sessionmaker(bind=engine)()
        session.connection().connection.set_isolation_level(0)
        session.execute('DROP DATABASE {}'.format(dbname))
        session.execute('CREATE DATABASE {}'.format(dbname))
        session.close()

        alembic_cfg = Config()
        alembic_cfg.set_main_option('script_location', 'versions')
        alembic_cfg.set_main_option('is_test', str(self.settings.get('is_test', False)))
        command.upgrade(alembic_cfg, "head")
