from unittest.mock import MagicMock
from unittest.mock import patch

from pytest import fixture
from pytest import raises

from qq.plugins.sqlalchemy.exceptions import SettingMissing
from qq.plugins.sqlalchemy.plugin import DatabasePlugin


class TestDatabasePlugin:
    @fixture
    def mapp(self):
        app = MagicMock()
        app.extra = {
            "settings": {
                "dbname": {
                    "url": "sqlite:///tmp.first.db",
                    "options": {"optionkey": "option value"},
                }
            }
        }
        return app

    @fixture
    def mcreate_engine(self):
        with patch("qq.plugins.sqlalchemy.plugin.create_engine") as mock:
            yield mock

    @fixture
    def mmake_url(self):
        with patch("qq.plugins.sqlalchemy.plugin.make_url") as mock:
            yield mock

    @fixture
    def msessionmaker(self):
        with patch("qq.plugins.sqlalchemy.plugin.sessionmaker") as mock:
            yield mock

    @fixture
    def plugin(self):
        plugin = DatabasePlugin()
        plugin._set_key("dbname")
        return plugin

    @fixture
    def metadata(self):
        return MagicMock()

    def test_start(self, plugin, mapp, msessionmaker, mcreate_engine):
        """
        .start should create proper sqlalchemy engine.
        """
        plugin.start(mapp)

        mcreate_engine.assert_called_once_with(
            "sqlite:///tmp.first.db", optionkey="option value"
        )

        assert plugin.sessionmaker == msessionmaker.return_value
        msessionmaker.assert_called_once_with(
            autoflush=False, autocommit=False, bind=mcreate_engine.return_value
        )

    def test_enter(self, plugin):
        """
        .enter should create new database session and assign it to the context
        """
        plugin.sessionmaker = MagicMock()
        mcontext = MagicMock()
        plugin.engine = MagicMock()

        assert plugin.enter(mcontext) == plugin.sessionmaker.return_value

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

    def test_dbname(self, plugin, mapp, msessionmaker, mcreate_engine):
        """
        .dbname should return name of the database made from the db url
        """
        plugin.start(mapp)

        assert plugin.dbname == "tmp.first.db"

    def test_validate_settings(self, plugin, mapp):
        """
        Starting plugin should raise an error when settings are not properly
        configured (missing url)
        """
        del mapp.extra["settings"]["dbname"]["url"]
        with raises(SettingMissing):
            plugin.start(mapp)

    def test_recreate(self, plugin, metadata, mcreate_engine, mapp):
        """
        .recreate should drop all and create all tables using provided metadata.
        """

        plugin.start(mapp)
        plugin.recreate(metadata)

        metadata.drop_all.assert_called_once_with(mcreate_engine.return_value)
        metadata.create_all.assert_called_once_with(mcreate_engine.return_value)
