from mock import MagicMock
from mock import call
from mock import patch
from mock import sentinel
from pytest import fixture

from qapla.database import DatabaseApplication
from qapla.database import DatabaseConfig
from qapla.database import DatabaseGenerator


class TestDatabaseConfig(object):

    @fixture
    def settings(self):
        return {}

    @fixture
    def paths(self):
        return {}

    @fixture
    def mconfig(self):
        return MagicMock()

    @fixture
    def database(self, mconfig, settings, paths):
        return DatabaseConfig(mconfig, settings, paths)

    @fixture
    def mget_engine(self, database):
        with patch.object(database, 'get_engine') as mock:
            yield mock

    @fixture
    def msessionmaker(self):
        with patch('qapla.database.sessionmaker') as mock:
            yield mock

    @fixture
    def mget_url(self, database):
        with patch.object(database, 'get_url') as mock:
            yield mock

    @fixture
    def mcreate_engine(self):
        with patch('qapla.database.create_engine') as mock:
            yield mock

    @fixture
    def mdatabase_generator(self):
        with patch('qapla.database.DatabaseGenerator') as mock:
            yield mock

    @fixture
    def malembic_config(self):
        with patch('qapla.database.Config') as mock:
            yield mock

    @fixture
    def mcommand(self):
        with patch('qapla.database.command') as mock:
            yield mock

    def test_build(self, database, mget_engine, msessionmaker, mconfig, mdatabase_generator):
        """
        .build should append sessionmaker to a registry and add database generator to the request object
        """
        database.build()

        mget_engine.assert_called_once_with()
        msessionmaker.assert_called_once_with(bind=mget_engine.return_value)
        assert mconfig.registry.dbmaker == msessionmaker.return_value
        mconfig.add_request_method.assert_called_once_with(
            mdatabase_generator.return_value,
            name='database',
            reify=True)

    def test_get_engine(self, database, mget_url, mcreate_engine, settings):
        """
        .get_engine should create sqlalchemy engine from application's settings
        """
        settings['db:options'] = {'one': 1, 'two': '2', 'three': 'three'}
        assert database.get_engine() == mcreate_engine.return_value

        mget_url.assert_called_once_with(None)
        mcreate_engine.assert_called_once_with(
            mget_url.return_value,
            one=1,
            two='2',
            three='three')

    def test_get_url(self, database, settings):
        """
        .get_url should create sqlalchemy's database url from application's settings
        """
        settings['db:type'] = 'postgresql'
        settings['db:login'] = 'mylogin'
        settings['db:password'] = 'mypassword'
        settings['db:host'] = 'google.pl'
        settings['db:port'] = '123'
        settings['db:name'] = 'superdb'

        assert database.get_url() == 'postgresql://mylogin:mypassword@google.pl:123/superdb'

    def test_recreate(
        self,
        database,
        settings,
        paths,
        mget_engine,
        msessionmaker,
        malembic_config,
        mcommand,
    ):
        """
        .recreate should connect to a different db, then drop and create configured one. After that it should start
        migration.
        """
        settings['db:name'] = 'mydbname'
        paths['backend:ini'] = '/stairway/to/heaven'

        database.recreate()

        mget_engine.assert_called_once_with('postgres')
        msessionmaker.assert_called_once_with(bind=mget_engine.return_value)
        msessionmaker.return_value.assert_called_once_with()
        session = msessionmaker.return_value.return_value
        session.connection.assert_called_once_with()
        session.connection.return_value.connection.set_isolation_level.assert_called_once_with(0)
        assert session.execute.call_args_list == [
            call('DROP DATABASE mydbname'),
            call('CREATE DATABASE mydbname'),
        ]
        session.close.assert_called_once_with()

        malembic_config.assert_called_once_with('/stairway/to/heaven', ini_section='alembic_test')
        mcommand.upgrade(malembic_config.return_value, "head")


class TestDatabaseGenerator(object):

    @fixture
    def generator(self):
        return DatabaseGenerator()

    @fixture
    def mrequest(self):
        return MagicMock()

    @fixture
    def msession(self, generator):
        generator.session = MagicMock()
        return generator.session

    def test_call(self, generator, mrequest):
        """
        .__call__ should create new session and add cleanup step for it.
        """
        assert generator(mrequest) == mrequest.registry.dbmaker.return_value

        mrequest.registry.dbmaker.assert_called_once_with()
        mrequest.add_finished_callback(generator.cleanup)

    def test_cleanup_on_exception(self, generator, msession, mrequest):
        """
        .cleanup should rollback database changes on exception
        """
        mrequest.exception = True

        generator.cleanup(mrequest)
        msession.rollback.assert_called_once_with()
        msession.close.assert_called_once_with()

    def test_cleanup_on_success(self, generator, msession, mrequest):
        """
        .cleanup should commit changes on response success
        """
        mrequest.exception = None

        generator.cleanup(mrequest)
        msession.commit.assert_called_once_with()
        msession.close.assert_called_once_with()


class TestDatabaseApplication(object):

    @fixture
    def app(self):
        return DatabaseApplication()

    @fixture
    def mdatabase_config(self):
        with patch('qapla.database.DatabaseConfig') as mock:
            yield mock

    def test_add_database(self, app, mdatabase_config):
        """
        .add_database should add database config to the pyramid application.
        """
        app.config = sentinel.config
        app.settings = sentinel.settings
        app.paths = sentinel.paths

        app.add_database()

        mdatabase_config.assert_called_once_with(
            sentinel.config,
            sentinel.settings,
            sentinel.paths)
        mdatabase_config.return_value.build.assert_called_once_with()
