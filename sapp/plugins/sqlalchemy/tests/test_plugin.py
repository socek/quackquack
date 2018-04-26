from unittest.mock import MagicMock
from unittest.mock import patch

from pytest import fixture

from sapp.plugins.sqlalchemy.plugin import DatabasePlugin


class TestDatabasePlugin(object):
    @fixture
    def mconfigurator(self):
        config = MagicMock()
        config.settings = {
            'db:dbname:url': 'sqlite:///tmp.first.db',
            'db:dbname:default_url': 'sqlite:///tmp.second.db',
            'db:dbname:options': {
                'optionkey': 'option value'
            }
        }
        config.dbplugins = {}
        return config

    @fixture
    def mcreate_engine(self):
        with patch('sapp.plugins.sqlalchemy.plugin.create_engine') as mock:
            yield mock

    @fixture
    def mmake_url(self):
        with patch('sapp.plugins.sqlalchemy.plugin.make_url') as mock:
            yield mock

    @fixture
    def msessionmaker(self):
        with patch('sapp.plugins.sqlalchemy.plugin.sessionmaker') as mock:
            yield mock

    @fixture
    def plugin(self):
        return DatabasePlugin('dbname')

    def test_start(self, plugin, mconfigurator, msessionmaker, mcreate_engine):
        """
        .start should create proper sqlalchemy engine.
        """
        plugin.start(mconfigurator)

        mcreate_engine.assert_called_once_with(
            'sqlite:///tmp.first.db', optionkey='option value')

        assert plugin.sessionmaker == msessionmaker.return_value
        msessionmaker.assert_called_once_with(
            autoflush=False,
            autocommit=False,
            bind=mcreate_engine.return_value)
        assert mconfigurator.dbplugins['dbname'] == plugin

    def test_enter(self, plugin):
        """
        .enter should create new database session and assign it to the context
        """
        plugin.sessionmaker = MagicMock()
        mcontext = MagicMock()

        plugin.enter(mcontext)

        assert mcontext.dbname == plugin.sessionmaker.return_value
        plugin.sessionmaker.assert_called_once_with()

    def test_exit(self, plugin):
        """
        .exit should close the database session.
        """
        plugin.dbsession = MagicMock()

        plugin.exit(None, None, None, None)

        assert not plugin.dbsession.rollback.called
        plugin.dbsession.close.assert_called_once_with()

    def test_exit_with_traceback(self, plugin):
        """
        .exit should rollback and close the database session when exception
        occured.
        """
        plugin.dbsession = MagicMock()

        plugin.exit(None, True, None, None)

        plugin.dbsession.rollback.assert_called_once_with()
        plugin.dbsession.close.assert_called_once_with()

    def test_get_dbname(self, plugin, mconfigurator, msessionmaker, mcreate_engine):
        """
        .get_dbname should return name of the database made from the db url
        """
        plugin.start(mconfigurator)

        assert plugin.get_dbname() == 'tmp.first.db'
