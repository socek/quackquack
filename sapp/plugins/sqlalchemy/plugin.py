from sqlalchemy.engine import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import sessionmaker

from sapp.application import Application
from sapp.context import Context
from sapp.plugins.settings import SettingsBasedPlugin
from sapp.plugins.sqlalchemy.exceptions import SettingMissing

URL_KEY = "url"
OPTIONS_KEY = "options"


class DatabasePlugin(SettingsBasedPlugin):
    DEFAULT_KEY = "db"

    @property
    def url(self):
        """
        Get url from settings.
        """
        return self._settings[URL_KEY]

    @property
    def dbname(self):
        return make_url(self.url).database

    def start(self, application: Application):
        self._settings = self.get_my_settings(application)
        self._validate_settings()
        self.engine = self.create_engine()
        self.sessionmaker = sessionmaker(
            autoflush=False, autocommit=False, bind=self.engine
        )
        return {
            "engine": self.engine,
            "sessionmaker": self.sessionmaker,
        }

    def enter(self, context: Context):
        return self.sessionmaker()

    def exit(self, context, exc_type, exc_value, traceback):
        if exc_type:
            self.dbsession.rollback()
        self.dbsession.close()

    def create_engine(self):
        return create_engine(self.url, **self._settings.get(OPTIONS_KEY, {}))

    def recreate(self, metadata):
        engine = self.create_engine()
        metadata.drop_all(engine)
        metadata.create_all(engine)

    def _validate_settings(self):
        if URL_KEY not in self._settings:
            raise SettingMissing(URL_KEY, self.name)
        make_url(self._settings[URL_KEY])
