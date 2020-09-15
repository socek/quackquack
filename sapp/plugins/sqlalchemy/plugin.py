from sqlalchemy.engine import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import sessionmaker

from sapp.plugins.sqlalchemy.consts import DATABASES_KEY
from sapp.plugins.sqlalchemy.consts import URL_KEY
from sapp.plugins.sqlalchemy.exceptions import SettingMissing


class DatabasePlugin(object):
    def __init__(self, name):
        self.name = name

    @property
    def url(self):
        """
        Get url from settings.
        """
        return self.settings[URL_KEY]

    @property
    def dbname(self):
        return make_url(self.url).database

    def start(self, configurator):
        alldbsettings = configurator.settings.setdefault(DATABASES_KEY, {})
        self.settings = alldbsettings.get(self.name, {})
        self._validate_settings()
        self.engine = self.create_engine()
        self.sessionmaker = sessionmaker(
            autoflush=False, autocommit=False, bind=self.engine
        )
        self._assign_to_configurator(configurator)

    def _assign_to_configurator(self, configurator):
        configurator.dbplugins = getattr(configurator, "dbplugins", {})
        configurator.dbplugins[self.name] = self

    def enter(self, context):
        self.dbsession = self.sessionmaker()
        setattr(context, self.name, self.dbsession)
        setattr(context, self.name + "_engine", self.engine)

    def exit(self, context, exc_type, exc_value, traceback):
        if exc_type:
            self.dbsession.rollback()
        self.dbsession.close()

    def create_engine(self):
        return create_engine(self.url, **self.settings.get("options", {}))

    def recreate(self, metadata):
        engine = self.create_engine()
        metadata.drop_all(engine)
        metadata.create_all(engine)

    def _validate_settings(self):
        if URL_KEY not in self.settings:
            raise SettingMissing(URL_KEY, self.name)
        make_url(self.settings[URL_KEY])
