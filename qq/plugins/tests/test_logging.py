from unittest.mock import sentinel

from pytest import fixture

from qq.plugins.logging import LoggingPlugin
from qq.testing import PluginFixtures

PREFIX = "qq.plugins.logging"


class TestLoggingPlugin(PluginFixtures):
    @fixture
    def plugin(self):
        plugin = LoggingPlugin()
        plugin.init("logging")
        return plugin

    @fixture
    def mdict_config(self, mocker):
        return mocker.patch(f"{PREFIX}.dictConfig")

    @fixture
    def mget_my_settings(self, mocker, plugin):
        mock = mocker.patch.object(plugin, "get_my_settings")
        mock.return_value = sentinel.logging
        return mock

    def test_start(self, plugin, mconfigurator, mdict_config, mget_my_settings):
        """
        .start should configure logging using settings
        """
        plugin.start(mconfigurator)

        mdict_config.assert_called_once_with(sentinel.logging)
