from mock import MagicMock
from pytest import fixture

from qapla.database.plugin import DatabasePlugin


class TestDatabasePlugin(object):

    @fixture
    def mdatabase(self):
        return MagicMock()

    @fixture
    def mapp(self):
        return MagicMock()

    @fixture
    def plugin(self, mapp, mdatabase):
        plugin = DatabasePlugin(mapp)
        plugin.add_database(mdatabase)
        return plugin

    def test_add_database(self, plugin, mapp, mdatabase):
        """
        .add_database should init database object and add it to the databases
        list.
        """
        assert mdatabase in plugin.databases.values()

    def test_add_to_app(self, plugin, mapp, mdatabase):
        """
        .add_to_app should validate settings for all databases and init them
        """
        plugin.add_to_app()

        mdatabase.add_to_app.assert_called_once_with(mapp)

    def test_add_to_web(self, plugin, mdatabase):
        """
        .add_to_app should add all databases to web.
        """
        plugin.add_to_web()

        mdatabase.add_to_web.assert_called_once_with()

    def test_getitem(self, plugin, mdatabase):
        """
        DatabasePlugin should return databases like a dict.
        """
        assert plugin[mdatabase.name] == mdatabase
