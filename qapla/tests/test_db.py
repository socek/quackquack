from mock import MagicMock
from mock import call
from mock import patch
from mock import sentinel
from pytest import fixture
from pytest import mark

from qapla.database import DatabaseApplication
from qapla.database import DatabasePlugin
from qapla.database import RequestDBSessionGenerator


class TestDatabasePlugin(object):

    @fixture
    def settings(self, mapp):
        mapp.settings = {
            'db:test_name': 'testname',
            'db:name': 'normalname',
        }
        return mapp.settings

    @fixture
    def paths(self, mapp):
        mapp.paths = {}
        return mapp.paths

    @fixture
    def mapp(self):
        return MagicMock()

    @fixture
    def database(self, mapp, settings, paths):
        return DatabasePlugin(mapp)

    @fixture
    def mconfig(self, mapp):
        mapp.config = MagicMock()
        return mapp.config

    @fixture
    def mget_engine(self, database):
        with patch.object(database, 'get_engine') as mock:
            yield mock

    @fixture
    def mget_url(self, database):
        with patch.object(database, 'get_url') as mock:
            yield mock

    @fixture
    def msessionmaker(self):
        with patch('qapla.database.sessionmaker') as mock:
            yield mock

    @fixture
    def mcreate_engine(self):
        with patch('qapla.database.create_engine') as mock:
            yield mock

    @fixture
    def mrequest_db_session_generator(self):
        with patch('qapla.database.RequestDBSessionGenerator') as mock:
            yield mock

    @fixture
    def malembic_config(self):
        with patch('qapla.database.Config') as mock:
            yield mock

    @fixture
    def mcommand(self):
        with patch('qapla.database.command') as mock:
            yield mock

    @mark.parametrize(
        'is_test, dbname_key',
        [
            [True, 'db:test_name'],
            [False, 'db:name'],
        ]
    )
    def test_init(self, mapp, settings, is_test, dbname_key):
        """
        DatabasePlugin should take different dbname depend on the is_test
        setting.
        """
        settings['is_test'] = is_test
        plugin = DatabasePlugin(mapp)

        assert plugin.app == mapp
        assert plugin.settings == settings
        assert plugin.paths == mapp.paths
        assert plugin.dbname == settings[dbname_key]

    def test_add_to_app(self, database, mget_engine, msessionmaker):
        """
        .add_to_app should create engine and session maker for app.
        """
        database.add_to_app()

        mget_engine.assert_called_once_with()
        msessionmaker.assert_called_once_with(bind=mget_engine.return_value)

        assert database.engine == mget_engine.return_value
        assert database.sessionmaker == msessionmaker.return_value

    def test_add_to_web(self, database, mconfig, mrequest_db_session_generator):
        """
        .add_to_web should append sessionmaker to a registry and add database
        generator to the request object
        """
        database.sessionmaker = sentinel.sessionmaker

        database.add_to_web()

        assert mconfig.registry.sessionmaker == sentinel.sessionmaker
        mconfig.add_request_method.assert_called_once_with(
            mrequest_db_session_generator.return_value,
            name='database',
            reify=True
        )
        mrequest_db_session_generator.assert_called_once_with()

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

    def test_get_url(self, mapp, settings):
        """
        .get_url should create sqlalchemy's database url from application's settings
        """
        settings['db:type'] = 'postgresql'
        settings['db:login'] = 'mylogin'
        settings['db:password'] = 'mypassword'
        settings['db:host'] = 'google.pl'
        settings['db:port'] = '123'
        settings['db:name'] = 'superdb'

        database = DatabasePlugin(mapp)

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
        database.recreate()

        mget_engine.assert_called_once_with('postgres')
        msessionmaker.assert_called_once_with(bind=mget_engine.return_value)
        msessionmaker.return_value.assert_called_once_with()
        session = msessionmaker.return_value.return_value
        session.connection.assert_called_once_with()
        session.connection.return_value.connection.set_isolation_level.assert_called_once_with(0)
        assert session.execute.call_args_list == [
            call('DROP DATABASE normalname'),
            call('CREATE DATABASE normalname'),
        ]
        session.close.assert_called_once_with()

        malembic_config.assert_called_once_with()
        mcommand.upgrade(malembic_config.return_value, "head")


class TestRequestDBSessionGenerator(object):

    @fixture
    def generator(self):
        return RequestDBSessionGenerator()

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
        assert generator(mrequest) == mrequest.registry.sessionmaker.return_value

        mrequest.registry.sessionmaker.assert_called_once_with()
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
    def mdatabase_plugin(self):
        with patch('qapla.database.DatabasePlugin') as mock:
            yield mock

    def test_add_database_app(self, app, mdatabase_plugin):
        """
        .add_database_app should add database config to the application.
        """
        app.add_database_app()

        mdatabase_plugin.assert_called_once_with(app)
        mdatabase_plugin.return_value.add_to_app.assert_called_once_with()
        assert app._db_plugin == mdatabase_plugin.return_value

    def test_add_database_web(self, app):
        """
        .add_database_web should add database config to the pyramid application.
        """
        app._db_plugin = MagicMock()
        app.add_database_web()

        app._db_plugin.add_to_web.assert_called_once_with()
