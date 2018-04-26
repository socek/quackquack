from unittest.mock import MagicMock
from unittest.mock import call
from unittest.mock import patch

from pytest import fixture

from sapp.plugins.sqlalchemy.recreate import RecreateDatabases


class TestRecreateDatabases(object):
    @fixture
    def mconfigurator(self):
        return MagicMock()

    @fixture
    def recreate(self, mconfigurator):
        return RecreateDatabases(mconfigurator)

    @fixture
    def mcommand(self):
        with patch('sapp.plugins.sqlalchemy.recreate.command') as mock:
            yield mock

    @fixture
    def mconfig(self):
        with patch('sapp.plugins.sqlalchemy.recreate.Config') as mock:
            yield mock

    @fixture
    def msessionmaker(self):
        with patch('sapp.plugins.sqlalchemy.recreate.sessionmaker') as mock:
            yield mock

    @fixture
    def mclear_database(self, recreate):
        with patch.object(recreate, '_clear_database') as mock:
            yield mock

    @fixture
    def mmigrate(self, recreate):
        with patch.object(recreate, '_migrate') as mock:
            yield mock

    def test_migrate(self, recreate, mconfig, mcommand):
        """
        ._migrate should run alembic's migration command
        """
        config = mconfig.return_value

        recreate._migrate('/tmp/to/something')

        mconfig.assert_called_once_with()

        assert config.set_main_option.call_args_list == [
            call('script_location', '/tmp/to/something'),
            call('is_test', 'true')
        ]
        mcommand.upgrade.assert_called_once_with(config, "head")

    def test_clear_database(self, recreate, msessionmaker):
        """
        ._clear_database should drop and create the old database.
        """
        mdb = MagicMock()
        mdb.get_dbname.return_value = 'lenin'
        session = msessionmaker.return_value.return_value

        recreate._clear_database(mdb)

        mdb.get_dbname.assert_called_once_with()
        mdb.get_engine.assert_called_once_with(default_url=True)

        msessionmaker.assert_called_once_with(bind=mdb.get_engine.return_value)
        msessionmaker.return_value.assert_called_once_with()

        session.connection.assert_called_once_with()
        (session.connection.return_value.connection.set_isolation_level.
         assert_called_once_with(0))
        assert session.execute.call_args_list == [
            call('DROP DATABASE IF EXISTS lenin'),
            call('CREATE DATABASE lenin')
        ]
        session.close.assert_called_once_with()

    def test_make(self, recreate, mclear_database, mmigrate, mconfigurator):
        """
        .make should recreate all appended databases.
        """
        mdb = MagicMock()
        mconfigurator.dbplugins = {'lenin': mdb}
        recreate.append_database('lenin', '/tmp/to/something')

        recreate.make()

        mclear_database.assert_called_once_with(mdb)
        mmigrate.assert_called_once_with('/tmp/to/something')

