from mock import patch
from mock import sentinel
from pytest import fixture

from sapp.plugins.settings import SettingsPlugin
from sapp.testing import PluginFixtures


class TestSettingsPlugin(PluginFixtures):
    MODULE = sentinel.settings_module

    @fixture
    def plugin(self, mfactory):
        return SettingsPlugin(self.MODULE)

    @fixture
    def mfactory(self):
        with patch('sapp.plugins.settings.Factory') as mock:
            yield mock

    def test_start_plugin(self, plugin, mfactory, mconfigurator):
        """
        .start_plugin should create settings for provided method, which is set
        in the configurator.
        """
        mconfigurator.method = 'pyramid'
        mfactory.return_value.make_settings.return_value = [
            sentinel.settings, sentinel.paths
        ]

        plugin.start_plugin(mconfigurator)

        mfactory.asset_called_once_with(self.MODULE)
        mfactory.return_value.make_settings.asset_called_once_with(
            settings={}, additional_modules=plugin.METHODS['pyramid'])

        assert plugin.settings == mconfigurator.settings == sentinel.settings
        assert plugin.paths == mconfigurator.paths == sentinel.paths

    def test_application(self, plugin, mapplication):
        """
        .enter should add settings and paths to the application.
        """
        plugin.settings = sentinel.settings
        plugin.paths = sentinel.paths

        plugin.enter(mapplication)

        assert mapplication.settings == sentinel.settings
        assert mapplication.paths == sentinel.paths
