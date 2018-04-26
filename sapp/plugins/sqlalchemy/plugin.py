from sqlalchemy.engine import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import sessionmaker

from sapp.plugins.sqlalchemy.database import DatabaseSetting


class DatabasePlugin(object):
    def __init__(self, name):
        self.name = name
        self._engine = None
        self._sessionmaker = None

    def start(self, configurator):
        self.settings = DatabaseSetting(configurator.settings, self.name)
        self.settings.validate()
        self.engine = self.get_engine()
        self.sessionmaker = sessionmaker(
            autoflush=False, autocommit=False, bind=self.engine)
        self._assign_to_configurator(configurator)

    def _assign_to_configurator(self, configurator):
        configurator.dbplugins = getattr(configurator, 'dbplugins', {})
        configurator.dbplugins[self.name] = self

    def enter(self, context):
        self.dbsession = self.sessionmaker()
        setattr(context, self.name, self.dbsession)

    def exit(self, context, exc_type, exc_value, traceback):
        if exc_type:
            self.dbsession.rollback()
        self.dbsession.close()

    def get_engine(self, default_url=False):
        url = self.get_url(default_url)
        return create_engine(url, **self.settings.get('options', {}))

    def get_dbname(self):
        """
        Get database name.
        """
        return make_url(self.get_url()).database

    def get_url(self, default_url=False):
        """
        Get url from settings.
        """
        subkey = 'default_url' if default_url else 'url'
        return self.settings[subkey]
