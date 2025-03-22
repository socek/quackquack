from typing import Dict

from sqlalchemy.engine import Engine
from sqlalchemy.engine import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import Session

from qq.application import Application
from qq.context import Context
from qq.plugins.settings import SettingsBasedPlugin
from qq.plugins.sqlalchemy.consts import ENGINE_KEY
from qq.plugins.sqlalchemy.consts import OPTIONS_KEY
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
        return {
            ENGINE_KEY: self.engine,
        }

    def enter(self, context: Context) -> Session:
        return Session(self.engine, expire_on_commit=False)

    def create_engine(self) -> Engine:
        return create_engine(self.url, **self._settings.get(OPTIONS_KEY, {}))

    def _validate_settings(self):
        if URL_KEY not in self._settings:
            raise SettingMissing(URL_KEY, self.key)
        make_url(self._settings[URL_KEY])


class SqlAlchemyPluginAsync(SqlAlchemyPlugin):

    def enter(self, context: Context) -> Session:
        return AsyncSession(self.engine, expire_on_commit=False)

    def create_engine(self) -> Engine:
        return create_async_engine(
            self.url, **self._settings.get(OPTIONS_KEY, {})
        )
