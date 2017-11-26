from mock import MagicMock
from mock import call
from mock import patch
from mock import sentinel
from pytest import fixture
from pytest import mark
from pytest import raises
from sqlalchemy.exc import ArgumentError

from qapla.database.database import ConfigurationError
from qapla.database.database import Database
from qapla.database.database import DatabaseSetting
from qapla.database.exceptions import SettingMissing


class TestDatabase(object):

    NAME = 'dbname'

    @fixture
    def database(self):
        return Database(self.NAME)

    @fixture
    def mapp(
        self,
        database,
        mget_engine,
        mdatabase_setting,
        msessionmaker,
        mscoped_session,
    ):
        mapp = MagicMock()
        database.add_to_app(mapp)
        return mapp

    @fixture
    def mget_engine(self, database):
        with patch.object(database, 'get_engine') as mock:
            yield mock

    @fixture
    def mget_url(self, database):
        with patch.object(database, 'get_url') as mock:
            yield mock

    @fixture
    def mclear_database(self, database):
        with patch.object(database, '_clear_database') as mock:
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

    @fixture
    def mdatabase_setting(self):
        with patch('qapla.database.database.DatabaseSetting') as mock:
            yield mock

    @fixture
    def mscoped_session(self):
        with patch('qapla.database.database.scoped_session') as mock:
            yield mock

    def test_add_to_app(
        self,
        database,
        mget_engine,
        msessionmaker,
        mdatabase_setting,
        mscoped_session,
    ):
        """
        .add_to_app should create engine and sessionmaker.
        """
        mapp = MagicMock()

        database.add_to_app(mapp)

        assert database.app is mapp
        assert database.settings is mdatabase_setting.return_value
        assert database.engine is mget_engine.return_value
        assert database.sessionmaker is mscoped_session.return_value
        mget_engine.assert_called_once_with()
        msessionmaker.assert_called_once_with(bind=database.engine)
        mdatabase_setting.assert_called_once_with(mapp.settings, self.NAME)
        mdatabase_setting.return_value.validate.assert_called_once_with()
        mscoped_session.assert_called_once_with(msessionmaker.return_value)

    def test_add_to_web(
        self,
        database,
        mapp,
        mrequest_dbsession_generator,
        msessionmaker,
        mscoped_session,
    ):
        """
        .add_to_web should add sessionmaker to request
        """
        mapp.config.registry = {}

        database.add_to_web()

        assert mapp.config.registry == {self.NAME: mscoped_session.return_value}
        mrequest_dbsession_generator.assert_called_once_with(self.NAME)
        mapp.config.add_request_method.assert_called_once_with(
            mrequest_dbsession_generator.return_value,
            name=self.NAME,
            reify=True)
        mscoped_session.assert_called_once_with(msessionmaker.return_value)

    def test_add_to_web_when_no_app(
        self,
        database,
    ):
        """
        .add_to_web should raise an error if called before .add_to_app
        """
        database.app = None
        with raises(ConfigurationError):
            database.add_to_web()

    @mark.parametrize(
        'default_url',
        [True, False],
    )
    def test_get_engine(self, database, mcreate_engine, mget_url, default_url):
        """
        .get_engine should get engine for database.
        """
        database.settings = {
            'options': {
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
            'url': False,
            'default_url': True,
        }

        assert database.get_url(default_url) == default_url

    def test_get_dbname(self, database):
        """
        .get_dbname should return name of the database from the url
        """
        database.settings = {
            'url': 'postgresql+pg8000://scott:tiger@localhost/mydbh'}

        assert database.get_dbname() == 'mydbh'

    def test_get_session(self, database):
        """
        .get_session should create session from sessionmaker.
        """
        database.sessionmaker = MagicMock()

        assert database.get_session() == database.sessionmaker.return_value
        database.sessionmaker.assert_called_once_with()

    def test_recreate(self, database, mclear_database, mmigrate):
        """
        .recreate should drop old database and run migrations from scratch.
        """
        database.recreate()

        mclear_database.assert_called_once_with()
        mmigrate.assert_called_once_with()

    def test_clear_database(
        self,
        database,
        mget_dbname,
        mget_engine,
        msessionmaker,
    ):
        """
        ._clear_database should drop database by connecting to default one (you
        can not drop database if you are connected to it) and dropping it.
        """
        session = msessionmaker.return_value.return_value
        mget_dbname.return_value = 'xena'

        database._clear_database()

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
            call('DROP DATABASE IF EXISTS xena'),
            call('CREATE DATABASE xena')]

        session.close.assert_called_once_with()

    def test_migrate(self, database, mconfig, mcommand):
        """
        ._migrate should create alembic config (in memory) and run migration
        from that config.
        """
        alembic_cfg = mconfig.return_value
        database.paths = MagicMock()

        database._migrate()

        mconfig.assert_called_once_with()
        assert alembic_cfg.set_main_option.call_args_list == [
            call(
                'script_location',
                database.paths.get.return_value),
            call(
                'is_test',
                'true')]
        mcommand.upgrade.assert_called_once_with(alembic_cfg, 'head')
        database.paths.get.assert_called_once_with('migrations')

    def test_close(self, database, msessionmaker):
        """
        .close should remove the session from the session maker.
        """
        database.sessionmaker = MagicMock()

        database.close()

        database.sessionmaker.remove.assert_called_once_with()


class TestDatabaseSetting(object):
    NAME = 'dbname'

    def test_validate_settings_on_missing(self):
        """
        ._validate_settings should raise an error when needed setting is not
        found.
        """
        settings = DatabaseSetting({}, 'dbname')

        with raises(SettingMissing):
            settings.validate()

    def test_validate_settings_on_bad_url(self):
        """
        ._validate_settings should raise an error when urls are not valid.
        """
        settings = {'db:dbname:url': 'badurl'}
        settings = DatabaseSetting(settings, 'dbname')

        with raises(ArgumentError):
            settings.validate()

    def test_validate_settings_on_success(self):
        """
        ._validate_settings should do nothing if settings are valid.
        """
        settings = {
            'db:dbname:url': 'postgresql://localhost/dbname',
            'db:dbname:default_url': 'postgresql://localhost/postgres'}
        settings = DatabaseSetting(settings, 'dbname')

        settings.validate()

    @mark.parametrize(
        'subkey, result',
        [
            ['subkey', 'db:dbname:subkey'],
            [None, 'db:dbname'],
        ])
    def test_get_key(self, subkey, result):
        """
        .get_key should return formatted key name for settings.
        """
        settings = DatabaseSetting({}, self.NAME)
        assert settings.get_key(subkey) == result

    def test_get_setting(self):
        """
        DatabaseSetting should act like a dict, whit generated names.
        """
        settings = DatabaseSetting({'db:dbname:key': sentinel.key}, self.NAME)

        assert settings['key'] is sentinel.key

    def test_set_setting(self):
        """
        DatabaseSetting should act like a dict, whit generated names.
        """
        settings = DatabaseSetting({'db:dbname:key': sentinel.key_value}, self.NAME)
        settings['key'] = sentinel.second_key_value

        assert settings['key'] is sentinel.second_key_value
        assert settings.settings == {'db:dbname:key': sentinel.second_key_value}

    def test_get_setting_with_default(self):
        """
        .get_setting should return default if not setting avalible
        """
        settings = DatabaseSetting({})

        assert settings.get('subkey', sentinel.default_key) is sentinel.default_key
