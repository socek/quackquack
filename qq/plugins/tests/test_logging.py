from unittest.mock import patch
from unittest.mock import sentinel

from pytest import fixture

from qq.plugins.logging import LoggingPlugin
from qq.testing import PluginFixtures


class TestLoggingPlugin(PluginFixtures):
    @fixture
    def plugin(self):
        return LoggingPlugin()

    @fixture
    def mdict_config(self):
        with patch("qq.plugins.logging.dictConfig") as mock:
            yield mock

    def test_start(self, plugin, mconfigurator, mdict_config):
        """
        .start should configure logging using settings
        """
        plugin._set_key("logging")
        mconfigurator.extra = {"settings": {"logging": sentinel.logging}}
        plugin.start(mconfigurator)

        mdict_config.assert_called_once_with(sentinel.logging)
