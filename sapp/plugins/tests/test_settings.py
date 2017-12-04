from mock import patch
from mock import sentinel
from pytest import fixture
from pytest import raises

from sapp.configurator import ExtraValueMissing
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

    def test_start(self, plugin, mfactory, mconfigurator):
        """
        .start should create settings for provided method, which is set
        in the configurator.
        """
        mconfigurator.extra = {plugin.EXTRA_KEY: 'pyramid'}
        mfactory.return_value.make_settings.return_value = [
            sentinel.settings, sentinel.paths
        ]

        plugin.start(mconfigurator)

        mfactory.asset_called_once_with(self.MODULE)
        mfactory.return_value.make_settings.asset_called_once_with(
            settings={}, additional_modules=plugin.METHODS['pyramid'])

        assert plugin.settings == mconfigurator.settings == sentinel.settings
        assert plugin.paths == mconfigurator.paths == sentinel.paths

    def test_start_when_extra_key_is_missing(self, plugin, mfactory,
                                             mconfigurator):
        """
        .start should raise an error when configurator does not have EXTRA_KEY
        in the extra dict.
        """
        mconfigurator.extra = {}
        mfactory.return_value.make_settings.return_value = [
            sentinel.settings, sentinel.paths
        ]

        with raises(ExtraValueMissing):
            plugin.start(mconfigurator)

        assert not mfactory.called

    def test_application(self, plugin, mapplication):
        """
        .enter should add settings and paths to the application.
        """
        plugin.settings = sentinel.settings
        plugin.paths = sentinel.paths

        plugin.enter(mapplication)

        assert mapplication.settings == sentinel.settings
        assert mapplication.paths == sentinel.paths
