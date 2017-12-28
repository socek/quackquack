from unittest.mock import patch
from unittest.mock import sentinel

from pytest import fixture

from sapp.plugins.logging import LoggingPlugin
from sapp.testing import PluginFixtures


class TestLoggingPlugin(PluginFixtures):
    @fixture
    def plugin(self):
        return LoggingPlugin()

    @fixture
    def mdict_config(self):
        with patch('sapp.plugins.logging.dictConfig') as mock:
            yield mock

    def test_start(self, plugin, mconfigurator, mdict_config):
        """
        .start should configure logging using settings
        """
        mconfigurator.settings = {'logging': sentinel.logging}
        plugin.start(mconfigurator)

        mdict_config.assert_called_once_with(sentinel.logging)
