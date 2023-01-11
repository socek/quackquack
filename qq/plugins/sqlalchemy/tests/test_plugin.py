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

    def test_start(
        self,
        plugin,
        mapp,
        mget_my_settings,
    ):
        """
        .start should create proper sqlalchemy engine.
        """
        plugin.start(mapp)

        assert plugin.engine is None
        assert plugin.session is None

    def test_enter_when_session_exists(self, plugin):
        """
        .enter should create new database session and assign it to the context
        """
        mcontext = MagicMock()
        plugin.engine = MagicMock()
        plugin.session = MagicMock()
        plugin.nest_index = 1

        assert plugin.enter(mcontext) == plugin.session
        assert plugin.nest_index == 2

    def test_enter_when_session_not_exists(
        self, plugin, mcreate_engine, msession
    ):
        """
        .enter should create new database session and assign it to the context
        """
        mcontext = MagicMock()
        plugin.session = None
        plugin.nest_index = 0
        plugin._settings = {
            "url": "sqlite:///tmp.first.db",
            "options": {"optionkey": "option value"},
        }

        assert plugin.enter(mcontext) == msession.return_value
        assert plugin.nest_index == 1
        assert plugin.session == msession.return_value
        assert plugin.engine == mcreate_engine.return_value

    def test_exit(self, plugin):
        """
        .exit should close the database session.
        """
        mengine = MagicMock()
        msession = MagicMock()
        plugin.engine = mengine
        plugin.session = msession
        plugin.nest_index = 1

        plugin.exit(None, None, None, None)

        assert not msession.rollback.called
        msession.close.assert_called_once_with()
        assert plugin.nest_index == 0
        mengine.dispose.assert_called_once_with()

    def test_exit_of_many_sessions(self, plugin):
        """
        .exit should decrease the index by one
        """
        plugin.engine = MagicMock()
        plugin.session = MagicMock()
        plugin.nest_index = 2

        plugin.exit(None, True, None, None)

        assert plugin.session.close.called is False
        assert plugin.nest_index == 1

    def test_exit_with_traceback(self, plugin):
        """
        .exit should rollback and close the database session when exception
        occured.
        """
        mengine = MagicMock()
        msession = MagicMock()
        plugin.engine = mengine
        plugin.session = msession
        plugin.nest_index = 1

        plugin.exit(None, True, None, None)

        msession.close.assert_called_once_with()
        assert plugin.nest_index == 0
        mengine.dispose.assert_called_once_with()

    def test_dbname(
        self,
        plugin,
        mapp,
        mcreate_engine,
        mget_my_settings,
        msession,
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

    def test_recreate(
        self, plugin, metadata, mcreate_engine, mapp, mget_my_settings
    ):
        """
        .recreate should drop all and create all tables using provided metadata.
        """

        plugin.start(mapp)
        plugin.recreate(metadata)

        metadata.drop_all.assert_called_once_with(mcreate_engine.return_value)
        metadata.create_all.assert_called_once_with(mcreate_engine.return_value)
