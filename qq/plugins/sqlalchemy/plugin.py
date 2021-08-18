from typing import Dict

from sqlalchemy.engine import Engine
from sqlalchemy.engine import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from qq.application import Application
from qq.context import Context
from qq.plugins.settings import SettingsBasedPlugin
from qq.plugins.sqlalchemy.consts import ENGINE_KEY
from qq.plugins.sqlalchemy.consts import OPTIONS_KEY
from qq.plugins.sqlalchemy.consts import SESSIONMAKER_KEY
from qq.plugins.sqlalchemy.consts import URL_KEY
from qq.plugins.sqlalchemy.exceptions import SettingMissing


class SqlAlchemyPlugin(SettingsBasedPlugin):
    @property
    def url(self):
        """
        Get url from settings.
        """
        return self._settings[URL_KEY]

    @property
    def dbname(self):
        return make_url(self.url).database

    def start(self, application: Application) -> Dict:
        self._settings = self.get_my_settings(application)
        self._validate_settings()
        self.engine = self.create_engine()
        self.sessionmaker = sessionmaker(
            autoflush=False, autocommit=False, bind=self.engine
        )
        return {
            ENGINE_KEY: self.engine,
            SESSIONMAKER_KEY: self.sessionmaker,
        }

    def enter(self, context: Context) -> Session:
        self.session = self.sessionmaker()
        return self.session

    def exit(self, context, exc_type, exc_value, traceback):
        if exc_type or self._settings.get("tests", False):
            self.session.rollback()
        self.session.close()

    def create_engine(self) -> Engine:
        return create_engine(self.url, **self._settings.get(OPTIONS_KEY, {}))

    def recreate(self, metadata):
        engine = self.create_engine()
        metadata.drop_all(engine)
        metadata.create_all(engine)

    def _validate_settings(self):
        if URL_KEY not in self._settings:
            raise SettingMissing(URL_KEY, self.key)
        make_url(self._settings[URL_KEY])
