from mock import MagicMock
from mock import sentinel
from pytest import fixture

from qapla.plugins.settings import SettingsPlugin


class PluginFixtures(object):
    @fixture
    def mconfigurator(self):
        return MagicMock()

    @fixture
    def mpyramid(self):
        return MagicMock()

    @fixture
    def mapplication(self):
        return MagicMock()


class TestSettingsPlugin(PluginFixtures):
    MODULE = sentinel.settings_module

    @fixture
    def mfactory(self):
        return MagicMock()

    @fixture
    def plugin(self, mfactory):
        return SettingsPlugin(self.MODULE, mfactory)

    def test_start_plugin(self, plugin, mfactory, mconfigurator):
        factory = mfactory.return_value
        factory.get_for.return_value = [sentinel.settings, sentinel.paths]

        plugin.start_plugin(mconfigurator)

        mfactory.assert_called_once_with(self.MODULE)
        factory.get_for.assert_called_once_with(mconfigurator.method)
        assert mconfigurator.settings == sentinel.settings
        assert mconfigurator.paths == sentinel.paths
        assert plugin.settings == sentinel.settings
        assert plugin.paths == sentinel.paths
        assert False
