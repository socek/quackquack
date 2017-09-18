from mock import MagicMock
from mock import call
from mock import patch
from mock import sentinel
from pytest import fixture
from pytest import mark
from pytest import raises

from qapla.database.exceptions import SettingMissing
from qapla.database.plugin import DatabasePlugin


class TestDatabasePlugin(object):

    @fixture
    def settings(self, mapp):
        mapp.settings = {
            'db:url': 'postgresql://scott:tiger@postgres/database',
            'db:test_url': 'postgresql://scott:tiger@postgres/database_test',
            'db:default_url': 'postgresql://scott:tiger@postgres/postgres',
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
    def mvalidate_settings(self, database):
        with patch.object(database, 'validate_settings') as mock:
            yield mock

    @fixture
    def msessionmaker(self):
        with patch('qapla.database.plugin.sessionmaker') as mock:
            yield mock

    @fixture
    def mcreate_engine(self):
        with patch('qapla.database.plugin.create_engine') as mock:
            yield mock

    @fixture
    def mrequest_db_session_generator(self):
        with patch('qapla.database.plugin.RequestDBSessionGenerator') as mock:
            yield mock

    @fixture
    def malembic_config(self):
        with patch('qapla.database.plugin.Config') as mock:
            yield mock

    @fixture
    def mcommand(self):
        with patch('qapla.database.plugin.command') as mock:
            yield mock

    @fixture
    def mmake_url(self):
        with patch('qapla.database.plugin.make_url') as mock:
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

    def test_add_to_app(
        self,
        database,
        mget_engine,
        msessionmaker,
        mvalidate_settings,
    ):
        """
        .add_to_app should create engine and session maker for app.
        """
        database.add_to_app()

        mget_engine.assert_called_once_with()
        msessionmaker.assert_called_once_with(bind=mget_engine.return_value)
        mvalidate_settings.assert_called_once_with()

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
        .get_url should get sqlalchemy's database url from application's settings
        """
        database = DatabasePlugin(mapp)

        settings[database.DB_KEY] = sentinel.db_url

        assert database.get_url() == sentinel.db_url

    def test_get_url_on_test(self, mapp, settings):
        """
        .get_url should get sqlalchemy's database url for test database if
        is_test is is set to True
        """
        database = DatabasePlugin(mapp)

        settings[database.DB_KEY] = sentinel.db_url
        settings[database.TEST_DB_KEY] = sentinel.test_db_url
        settings['is_test'] = True

        assert database.get_url() == sentinel.test_db_url

    def test_get_url_on_force(self, mapp, settings):
        """
        .get_url should get sqlalchemy's database url choosed by the args from
        application's settings
        """
        database = DatabasePlugin(mapp)

        settings[database.DB_KEY] = sentinel.db_url
        settings[database.TEST_DB_KEY] = sentinel.test_db_url

        assert database.get_url(database.TEST_DB_KEY) == sentinel.test_db_url

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

        mget_engine.assert_called_once_with(database.DEFAULT_DB_KEY)
        msessionmaker.assert_called_once_with(bind=mget_engine.return_value)
        msessionmaker.return_value.assert_called_once_with()
        session = msessionmaker.return_value.return_value
        session.connection.assert_called_once_with()
        session.connection.return_value.connection.set_isolation_level.assert_called_once_with(0)
        assert session.execute.call_args_list == [
            call('DROP DATABASE database'),
            call('CREATE DATABASE database'),
        ]
        session.close.assert_called_once_with()

        malembic_config.assert_called_once_with()
        mcommand.upgrade(malembic_config.return_value, "head")

    @mark.parametrize(
        "keys",
        [
            [],
            [DatabasePlugin.DB_KEY],
            [DatabasePlugin.DB_KEY, DatabasePlugin.TEST_DB_KEY],
        ]
    )
    def test_validate_settings(self, database, keys):
        """
        .validate_settings should raise error when one of the needed settings
        is missing.
        """
        database.settings = {}
        for key in keys:
            database.settings[key] = True

        with raises(SettingMissing):
            database.validate_settings()

    def test_validate_settings_validating_uris(self, database, settings, mmake_url):
        """
        .validate_settings should validate if database urls are valid.
        """
        database.validate_settings()

        assert mmake_url.call_args_list == [
            call(settings[database.DB_KEY]),
            call(settings[database.TEST_DB_KEY]),
            call(settings[database.DEFAULT_DB_KEY]),
        ]
