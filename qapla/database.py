from alembic import command
from alembic.config import Config
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from qapla.app import Application


class DatabasePlugin(object):

    def __init__(self, app):
        self.app = app
        self.settings = app.settings
        self.paths = app.paths

        if app.settings.get('is_test', False):
            self.dbname = self.settings['db:test_name']
        else:
            self.dbname = self.settings['db:name']

    def add_to_app(self):
        self.engine = self.get_engine()
        self.sessionmaker = sessionmaker(bind=self.engine)

    def add_to_web(self):
        self.app.config.registry.sessionmaker = self.sessionmaker
        self.app.config.add_request_method(
            RequestDBSessionGenerator(),
            name='database',
            reify=True)

    def get_engine(self, dbname=None):
        url = self.get_url(dbname)
        return create_engine(url, **self.settings['db:options'])

    def get_url(self, dbname=None):
        dbname = dbname or self.dbname
        return '{type}://{login}:{password}@{host}:{port}/{name}'.format(
            type=self.settings['db:type'],
            login=self.settings['db:login'],
            password=self.settings['db:password'],
            host=self.settings['db:host'],
            port=self.settings['db:port'],
            name=dbname)

    def recreate(self):
        """
        Drop old database and migrate from scratch.
        """
        engine = self.get_engine('postgres')
        session = sessionmaker(bind=engine)()
        session.connection().connection.set_isolation_level(0)
        session.execute('DROP DATABASE {}'.format(self.dbname))
        session.execute('CREATE DATABASE {}'.format(self.dbname))
        session.close()

        alembic_cfg = Config()
        alembic_cfg.set_main_option('script_location', 'versions')
        alembic_cfg.set_main_option('is_test', str(self.settings.get('is_test', False)))
        command.upgrade(alembic_cfg, "head")


class RequestDBSessionGenerator(object):

    def __call__(self, request):
        maker = request.registry.sessionmaker
        self.session = maker()
        request.add_finished_callback(self.cleanup)
        return self.session

    def cleanup(self, request):
        if request.exception is not None:
            self.session.rollback()
        else:
            # TODO: we need proper mechanism for handling sqlalchemy errors
            try:
                self.session.commit()
            except:
                self.session.rollback()
        self.session.close()


class DatabaseApplication(Application):

    def add_database_app(self):
        """
        Add sqlalchemy database to the Application.
        """
        self._db_plugin = DatabasePlugin(self)
        self._db_plugin.add_to_app()

    def add_database_web(self):
        """
        Add sqlalchemy database to the pyramid app.
        """
        self._db_plugin.add_to_web()
