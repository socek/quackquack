from unittest.mock import MagicMock
from unittest.mock import patch

from pytest import fixture
from pytest import raises

from sapp.plugins.sqlalchemy.consts import DATABASES_KEY
from sapp.plugins.sqlalchemy.exceptions import SettingMissing
from sapp.plugins.sqlalchemy.plugin import DatabasePlugin


class TestDatabasePlugin:
    @fixture
    def mconfigurator(self):
        config = MagicMock()
        config.settings = {
            DATABASES_KEY: {
                "dbname": {
                    "url": "sqlite:///tmp.first.db",
                    "options": {"optionkey": "option value"},
                }
            }
        }
        config.dbplugins = {}
        return config

    @fixture
    def mcreate_engine(self):
        with patch("sapp.plugins.sqlalchemy.plugin.create_engine") as mock:
            yield mock

    @fixture
    def mmake_url(self):
        with patch("sapp.plugins.sqlalchemy.plugin.make_url") as mock:
            yield mock

    @fixture
    def msessionmaker(self):
        with patch("sapp.plugins.sqlalchemy.plugin.sessionmaker") as mock:
            yield mock

    @fixture
    def plugin(self):
        return DatabasePlugin("dbname")

    @fixture
    def metadata(self):
        return MagicMock()

    def test_start(self, plugin, mconfigurator, msessionmaker, mcreate_engine):
        """
        .start should create proper sqlalchemy engine.
        """
        plugin.start(mconfigurator)

        mcreate_engine.assert_called_once_with(
            "sqlite:///tmp.first.db", optionkey="option value"
        )

        assert plugin.sessionmaker == msessionmaker.return_value
        msessionmaker.assert_called_once_with(
            autoflush=False, autocommit=False, bind=mcreate_engine.return_value
        )
        assert mconfigurator.dbplugins["dbname"] == plugin

    def test_enter(self, plugin):
        """
        .enter should create new database session and assign it to the context
        """
        plugin.sessionmaker = MagicMock()
        mcontext = MagicMock()
        plugin.engine = MagicMock()

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

    def test_dbname(self, plugin, mconfigurator, msessionmaker, mcreate_engine):
        """
        .dbname should return name of the database made from the db url
        """
        plugin.start(mconfigurator)

        assert plugin.dbname == "tmp.first.db"

    def test_validate_settings(self, plugin, mconfigurator):
        """
        Starting plugin should raise an error when settings are not properly
        configured (missing url)
        """
        del mconfigurator.settings[DATABASES_KEY]["dbname"]["url"]
        with raises(SettingMissing):
            plugin.start(mconfigurator)

    def test_recreate(self, plugin, metadata, mcreate_engine, mconfigurator):
        """
        .recreate should drop all and create all tables using provided metadata.
        """
        plugin.start(mconfigurator)
        plugin.recreate(metadata)

        metadata.drop_all.assert_called_once_with(mcreate_engine.return_value)
        metadata.create_all.assert_called_once_with(mcreate_engine.return_value)
