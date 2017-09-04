from alembic import command
from alembic.config import Config
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from qapla.app import Application


class DatabaseConfig(object):

    def __init__(self, config, settings, paths, dbname=None):
        self.config = config
        self.settings = settings
        self.paths = paths
        self.dbname = dbname

    def build(self):
        engine = self.get_engine(self.dbname)
        self.maker = self.get_maker(engine)
        self.config.registry.dbmaker = self.maker
        self.config.add_request_method(DatabaseGenerator(), name='database', reify=True)
        return self.maker

    def get_engine(self, dbname=None):
        url = self.get_url(dbname)
        return create_engine(url, **self.settings['db:options'])

    def get_maker(self, engine):
        return sessionmaker(bind=engine)

    def get_url(self, dbname=None):
        dbname = dbname or self.dbname or self.settings['db:name']
        return '{type}://{login}:{password}@{host}:{port}/{name}'.format(
            type=self.settings['db:type'],
            login=self.settings['db:login'],
            password=self.settings['db:password'],
            host=self.settings['db:host'],
            port=self.settings['db:port'],
            name=dbname)

    def recreate(self, for_test=True):
        if for_test:
            db = self.settings['db:name']
        else:
            db = self.settings['db:test_name']

        engine = self.get_engine('postgres')
        session = sessionmaker(bind=engine)()
        session.connection().connection.set_isolation_level(0)
        session.execute('DROP DATABASE {}'.format(db))
        session.execute('CREATE DATABASE {}'.format(db))
        session.close()

        alembic_cfg = Config()
        alembic_cfg.set_main_option('script_location', 'versions')
        alembic_cfg.set_main_option('dbname', db)
        command.upgrade(alembic_cfg, "head")


class DatabaseGenerator(object):

    def __call__(self, request):
        maker = request.registry.dbmaker
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

    def add_database(self):
        """
        Add sqlalchemy database to the pyramid app.
        """
        self._db_config = DatabaseConfig(self.config, self.settings, self.paths)
        self._db_config.build()
