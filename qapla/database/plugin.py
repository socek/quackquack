from sqlalchemy.engine import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from qapla.database.database import DatabaseSetting


class Database(object):
    def __init__(self, name):
        self.name = name
        self._engine = None
        self._session_maker = None

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

    def start_plugin(self, configurator):
        self.settings = DatabaseSetting(configurator.settings, self.name)
        self.settings.validate()

        configurator.database = self

    @property
    def engine(self):
        if not self._engine:
            self._engine = self.get_engine()
        return self._engine

    def _get_engine(self, default_url=False):
        url = self.get_url(default_url)
        return create_engine(url, **self.settings.get('options', {}))

    @property
    def session_maker(self):
        if not self._session_maker:
            self._session_maker = scoped_session(
                sessionmaker(bind=self.engine))
        return self._session_maker

    def enter(self, application):
        self.dbsession = self.session_maker()
        application.database = self
        application.dbsession = self.dbsession

    def exit(self, application, exc_type, exc_value, traceback):
        if exc_type:
            self.dbsession.rollback()
        self.session_maker.remove()
