from unittest.mock import MagicMock

from pytest import fixture
from pytest import raises

from qq.plugins.sqlalchemy.exceptions import SettingMissing
from qq.plugins.sqlalchemy.plugin import SqlAlchemyPlugin

PREFIX = "qq.plugins.sqlalchemy.plugin"


class TestSqlAlchemyPlugin:
    @fixture
    def mapp(self):
        return MagicMock()

    @fixture
    def mcreate_engine(self, mocker):
        return mocker.patch(f"{PREFIX}.create_engine")

    @fixture
    def mmake_url(self, mocker):
        return mocker.patch(f"{PREFIX}.make_url")

    @fixture
    def msessionmaker(self, mocker):
        return mocker.patch(f"{PREFIX}.sessionmaker")

    @fixture
    def plugin(self):
        plugin = SqlAlchemyPlugin()
        plugin.init("dbname")
        return plugin

    @fixture
    def mget_my_settings(self, mocker, plugin):
        mock = mocker.patch.object(plugin, "get_my_settings")
        mock.return_value = {
            "url": "sqlite:///tmp.first.db",
            "options": {"optionkey": "option value"},
        }
        return mock

    @fixture
    def metadata(self):
        return MagicMock()

    def test_start(
        self, plugin, mapp, msessionmaker, mcreate_engine, mget_my_settings
    ):
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
        plugin.session = MagicMock()
        plugin._settings = {
            "url": "sqlite:///tmp.first.db",
            "options": {"optionkey": "option value"},
        }

        plugin.exit(None, None, None, None)

        assert not plugin.session.rollback.called
        plugin.session.close.assert_called_once_with()

    def test_exit_with_traceback(self, plugin):
        """
        .exit should rollback and close the database session when exception
        occured.
        """
        plugin.session = MagicMock()

        plugin.exit(None, True, None, None)

        plugin.session.rollback.assert_called_once_with()
        plugin.session.close.assert_called_once_with()

    def test_dbname(self, plugin, mapp, msessionmaker, mcreate_engine, mget_my_settings):
        """
        .dbname should return name of the database made from the db url
        """
        plugin.start(mapp)

        assert plugin.dbname == "tmp.first.db"

    def test_validate_settings(self, plugin, mapp, mget_my_settings):
        """
        Starting plugin should raise an error when settings are not properly
        configured (missing url)
        """
        del mget_my_settings.return_value["url"]
        with raises(SettingMissing):
            plugin.start(mapp)

    def test_recreate(self, plugin, metadata, mcreate_engine, mapp, mget_my_settings):
        """
        .recreate should drop all and create all tables using provided metadata.
        """

        plugin.start(mapp)
        plugin.recreate(metadata)

        metadata.drop_all.assert_called_once_with(mcreate_engine.return_value)
        metadata.create_all.assert_called_once_with(mcreate_engine.return_value)
