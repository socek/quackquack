import os

from os.path import dirname

from pytest import fixture
from pytest import raises
from unittest.mock import MagicMock
from unittest.mock import patch
from unittest.mock import sentinel

from sapp.plugins.settings import PrefixedStringsDict
from sapp.plugins.settings import SettingsPlugin
from sapp.testing import PluginFixtures


class TestSettingsPlugin(PluginFixtures):
    MODULE = sentinel.settings_module

    @fixture
    def plugin(self):
        return SettingsPlugin(self.MODULE)

    @fixture
    def mstring_dict(self):
        return {}

    @fixture
    def mpaths(self):
        with patch('sapp.plugins.settings.PrefixedStringsDict') as mock:
            yield mock

    @fixture
    def mconfigurator(self):
        return MagicMock()

    @fixture
    def mimport(self, plugin):
        with patch.object(plugin, '_import') as mock:
            yield mock

    def test_application(self, plugin, mapplication, mconfigurator):
        """
        .enter should add settings and paths to the application.
        """
        plugin.configurator = mconfigurator
        plugin.configurator.settings = sentinel.settings

        plugin.enter(mapplication)

        assert mapplication.settings == sentinel.settings

    def test_import(self, plugin):
        assert plugin._import('os') == os

    def test_start(self, plugin, mconfigurator, mimport):
        """
        .start should gather settings for startpoint and push the data into
        configurator.
        """
        mconfigurator.startpoint = 'myapp'
        plugin.start(mconfigurator)

        mimport.assert_called_once_with(self.MODULE)
        mimport.return_value.myapp.assert_called_once_with()

        assert mconfigurator.settings == mimport.return_value.myapp.return_value


class TestPrefixedStringsDict(object):
    @fixture
    def paths(self):
        return PrefixedStringsDict()

    def test_set_prefix(self, paths):
        """
        .set_prefix should set prefix on the paths.
        """
        paths['name'] = 'come'
        assert paths['name'] == 'come'

        paths.set_prefix('myprefix/')
        assert paths['name'] == 'myprefix/come'

    def test_setitem_with_bad_value(self, paths):
        """
        PrefixedStringsDict can be set only by the str objects.
        """
        paths['name'] = 'key'

        with raises(ValueError):
            paths['name'] = 12

    def test_set_prefix_from_module(self, paths):
        """
        .set_prefix_from_module should set prefix from module dir path
        """
        paths.set_prefix_from_module(os)

        assert paths.prefix == dirname(os.__file__)

    def test_init_set_prefix_from_module(self):
        """
        init should allow to set prefix from module's dir
        """
        paths = PrefixedStringsDict(module=os)

        assert paths.prefix == dirname(os.__file__)
