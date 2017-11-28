from sqlalchemy.engine import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import sessionmaker

from sapp.database.database import DatabaseSetting


class Database(object):
    def __init__(self, name):
        self.name = name
        self._engine = None
        self._sessionmaker = None

    def start_plugin(self, configurator):
        self.settings = DatabaseSetting(configurator.settings, self.name)
        self.settings.validate()
        self.engine = self._get_engine()
        self.sessionmaker = sessionmaker(
            autoflush=False, autocommit=False, bind=self.engine)

        configurator.database = self

    def enter(self, application):
        self.dbsession = self.sessionmaker()
        application.database = self
        application.dbsession = self.dbsession

    def exit(self, application, exc_type, exc_value, traceback):
        if exc_type:
            self.dbsession.rollback()
        else:
            self.dbsession.commit()
        self.dbsession.close()

    def _get_engine(self, default_url=False):
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
