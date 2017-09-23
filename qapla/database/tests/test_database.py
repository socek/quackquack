from mock import MagicMock
from mock import call
from mock import patch
from mock import sentinel
from pytest import fixture
from pytest import mark
from pytest import raises
from sqlalchemy.exc import ArgumentError

from qapla.database.database import Database
from qapla.database.exceptions import SettingMissing


class TestDatabase(object):

    NAME = 'dbname'

    @fixture
    def database(self):
        return Database(self.NAME)

    @fixture
    def mapp(self, database, mget_engine, mvalidate_settings, msessionmaker):
        mapp = MagicMock()
        database.add_to_app(mapp)
        return mapp

    @fixture
    def mget_engine(self, database):
        with patch.object(database, 'get_engine') as mock:
            yield mock

    @fixture
    def mvalidate_settings(self, database):
        with patch.object(database, '_validate_settings') as mock:
            yield mock

    @fixture
    def mget_url(self, database):
        with patch.object(database, 'get_url') as mock:
            yield mock

    @fixture
    def mdrop_database(self, database):
        with patch.object(database, '_drop_database') as mock:
            yield mock

    @fixture
    def mmigrate(self, database):
        with patch.object(database, '_migrate') as mock:
            yield mock

    @fixture
    def mget_dbname(self, database):
        with patch.object(database, 'get_dbname') as mock:
            yield mock

    @fixture
    def msessionmaker(self):
        with patch('qapla.database.database.sessionmaker') as mock:
            yield mock

    @fixture
    def mrequest_dbsession_generator(self):
        with patch('qapla.database.database.RequestDBSessionGenerator') as mock:
            yield mock

    @fixture
    def mcreate_engine(self):
        with patch('qapla.database.database.create_engine') as mock:
            yield mock

    @fixture
    def mconfig(self):
        with patch('qapla.database.database.Config') as mock:
            yield mock

    @fixture
    def mcommand(self):
        with patch('qapla.database.database.command') as mock:
            yield mock

    def test_add_to_app(
        self,
        database,
        mget_engine,
        mvalidate_settings,
        msessionmaker,
    ):
        """
        .add_to_app should create engine and sessionmaker.
        """
        mapp = MagicMock()

        database.add_to_app(mapp)

        assert database.app is mapp
        assert database.settings is mapp.settings
        mvalidate_settings.assert_called_once_with()
        mget_engine.assert_called_once_with()
        assert database.engine is mget_engine.return_value
        msessionmaker.assert_called_once_with(bind=database.engine)
        assert database.sessionmaker is msessionmaker.return_value

    def test_add_to_web(
        self,
        database,
        mapp,
        mrequest_dbsession_generator,
        msessionmaker,
    ):
        """
        .add_to_web should add sessionmaker to request
        """
        mapp.config.registry = {}

        database.add_to_web()

        assert mapp.config.registry == {self.NAME: msessionmaker.return_value}
        mrequest_dbsession_generator.assert_called_once_with(self.NAME)
        mapp.config.add_request_method.assert_called_once_with(
            mrequest_dbsession_generator.return_value,
            name=self.NAME,
            reify=True)

    def test_validate_settings_on_missing(self, database):
        """
        ._validate_settings should raise an error when needed setting is not
        found.
        """
        database.settings = {}

        with raises(SettingMissing):
            database._validate_settings()

    def test_validate_settings_on_bad_url(self, database):
        """
        ._validate_settings should raise an error when urls are not valid.
        """
        database.settings = {'db:dbname:url': 'badurl'}

        with raises(ArgumentError):
            database._validate_settings()

    def test_validate_settings_on_success(self, database):
        """
        ._validate_settings should do nothing if settings are valid.
        """
        database.settings = {
            'db:dbname:url': 'postgresql://localhost/dbname',
            'db:dbname:default_url': 'postgresql://localhost/postgres'}

        database._validate_settings()

    @mark.parametrize(
        'subkey, result',
        [
            ['subkey', 'db:dbname:subkey'],
            [None, 'db:dbname'],
        ])
    def test_get_key(self, database, subkey, result):
        """
        .get_key should return formatted key name for settings.
        """
        assert database._get_key(subkey) == result

    def test_get_setting(self, database):
        """
        .get_setting should get key from setting
        """
        database.settings = {'db:dbname:key': sentinel.key}

        assert database.get_setting('key') is sentinel.key

    def test_get_setting_with_default(self, database):
        """
        .get_setting should return default if not setting avalible
        """
        database.settings = {}

        assert database.get_setting('subkey', sentinel.default_key) is sentinel.default_key

    @mark.parametrize(
        'default_url',
        [True, False],
    )
    def test_get_engine(self, database, mcreate_engine, mget_url, default_url):
        """
        .get_engine should get engine for database.
        """
        database.settings = {
            'db:dbname:options': {
                'something': sentinel.something}}

        assert database.get_engine(default_url) == mcreate_engine.return_value
        mcreate_engine.assert_called_once_with(
            mget_url.return_value,
            something=sentinel.something)
        mget_url.assert_called_once_with(default_url)

    @mark.parametrize(
        'default_url',
        [True, False],
    )
    def test_get_url(self, database, default_url):
        """
        .get_url should get url from settings.
        """
        database.settings = {
            'db:dbname:url': False,
            'db:dbname:default_url': True,
        }

        assert database.get_url(default_url) == default_url

    def test_get_dbname(self, database):
        """
        .get_dbname should return name of the database from the url
        """
        database.settings = {
            'db:dbname:url': 'postgresql+pg8000://scott:tiger@localhost/mydbh'}

        assert database.get_dbname() == 'mydbh'

    def test_get_session(self, database):
        """
        .get_session should create session from sessionmaker.
        """
        database.sessionmaker = MagicMock()

        assert database.get_session() == database.sessionmaker.return_value
        database.sessionmaker.assert_called_once_with()

    def test_recreate(self, database, mdrop_database, mmigrate):
        """
        .recreate should drop old database and run migrations from scratch.
        """
        database.recreate()

        mdrop_database.assert_called_once_with()
        mmigrate.assert_called_once_with()

    def test_drop_database(
        self,
        database,
        mget_dbname,
        mget_engine,
        msessionmaker,
    ):
        """
        ._drop_database should drop database by connecting to default one (you
        can not drop database if you are connected to it) and dropping it.
        """
        session = msessionmaker.return_value.return_value
        mget_dbname.return_value = 'xena'

        database._drop_database()

        mget_dbname.assert_called_once_with()
        mget_engine.assert_called_once_with(True)
        msessionmaker.assert_called_once_with(bind=mget_engine.return_value)
        msessionmaker.return_value.assert_called_once_with()

        session.connection.assert_called_once_with()
        (
            session
            .connection
            .return_value
            .connection
            .set_isolation_level
            .assert_called_once_with(0))
        assert session.execute.call_args_list == [
            call('DROP DATABASE xena'),
            call('CREATE DATABASE xena')]

        session.close.assert_called_once_with()

    def test_migrate(self, database, mconfig, mcommand):
        """
        ._migrate should create alembic config (in memory) and run migration
        from that config.
        """
        alembic_cfg = mconfig.return_value

        database._migrate()

        mconfig.assert_called_once_with()
        assert alembic_cfg.set_main_option.call_args_list == [
            call(
                'script_location',
                'versions'),
            call(
                'db_app_name',
                database.name)]
        mcommand.upgrade.assert_called_once_with(alembic_cfg, 'head')
