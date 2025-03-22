from unittest.mock import MagicMock

from pytest import fixture
from pytest import raises

from qq.plugins.sqlalchemy.exceptions import SettingMissing
from qq.plugins.sqlalchemy.plugin import SqlAlchemyPlugin
from qq.plugins.sqlalchemy.plugin import SqlAlchemyPluginAsync

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
    def msession(self, mocker):
        return mocker.patch(f"{PREFIX}.Session")

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

    def test_start(self, plugin, mapp, mcreate_engine, mget_my_settings):
        """
        .start should create proper sqlalchemy engine.
        """
        plugin.start(mapp)

        mcreate_engine.assert_called_once_with(
            "sqlite:///tmp.first.db", optionkey="option value"
        )

    def test_dbname(
        self,
        plugin,
        mapp,
        mcreate_engine,
        mget_my_settings,
    ):
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

    def test_enter(self, plugin, msession):
        """
        .enter should create new database session and assign it to the context
        """
        mcontext = MagicMock()
        plugin.engine = MagicMock()

        assert plugin.enter(mcontext) == msession.return_value
        msession.assert_called_once_with(plugin.engine, expire_on_commit=False)


class TestSqlAlchemyPluginAsync:
    @fixture
    def mapp(self):
        return MagicMock()

    @fixture
    def masync_session(self, mocker):
        return mocker.patch(f"{PREFIX}.AsyncSession")

    @fixture
    def mcreate_async_engine(self, mocker):
        return mocker.patch(f"{PREFIX}.create_async_engine")

    @fixture
    def plugin(self):
        plugin = SqlAlchemyPluginAsync()
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

    def test_enter(self, plugin, masync_session):
        """
        .enter should create new database session and assign it to the context
        """
        mcontext = MagicMock()
        plugin.engine = MagicMock()

        assert plugin.enter(mcontext) == masync_session.return_value
        masync_session.assert_called_once_with(
            plugin.engine, expire_on_commit=False
        )

    def test_start(self, plugin, mapp, mcreate_async_engine, mget_my_settings):
        """
        .start should create proper sqlalchemy engine.
        """
        plugin.start(mapp)

        mcreate_async_engine.assert_called_once_with(
            "sqlite:///tmp.first.db", optionkey="option value"
        )
