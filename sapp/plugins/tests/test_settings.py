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
    def mgather_settings_for_startpoint(self, plugin):
        with patch.object(plugin, '_gather_settings_for_startpoint') as mock:
            yield mock

    @fixture
    def mpush_settings_to_configurator(self, plugin):
        with patch.object(plugin, 'push_settings_to_configurator') as mock:
            yield mock

    @fixture
    def mcreate_settings(self, plugin):
        with patch.object(plugin, 'create_settings') as mock:
            yield mock

    @fixture
    def mimport(self, plugin):
        with patch.object(plugin, '_import') as mock:
            yield mock

    @fixture
    def mgenerate_settings(self, plugin):
        with patch.object(plugin, '_generate_settings') as mock:
            yield mock

    def test_application(self, plugin, mapplication):
        """
        .enter should add settings and paths to the application.
        """
        plugin.settings = sentinel.settings
        plugin.paths = sentinel.paths

        plugin.enter(mapplication)

        assert mapplication.settings == sentinel.settings
        assert mapplication.paths == sentinel.paths

    def test_create_settings(self, plugin, mstring_dict, mpaths):
        """
        .create_settings should create SettingsDict and PrefixedStringsDictDict.
        """
        plugin.create_settings() == [mstring_dict, mpaths.return_value]
        mpaths.assert_called_once_with()

    def test_import(self, plugin):
        assert plugin._import('os') == os

    def test_start(self, plugin, mconfigurator,
                   mgather_settings_for_startpoint,
                   mpush_settings_to_configurator):
        """
        .start should gather settings for startpoint and push the data into
        configurator.
        """
        plugin.start(mconfigurator)

        mgather_settings_for_startpoint.assert_called_once_with(
            mconfigurator.startpoint)
        mpush_settings_to_configurator.assert_called_once_with(
            mconfigurator, mgather_settings_for_startpoint.return_value)

    def test_push_settings_to_configurator(self, plugin, mconfigurator):
        """
        .push_settings_to_configurator should set settings from the dict
        into the configurator.
        """
        settings = dict(settings=sentinel.settings, paths=sentinel.paths)

        plugin.push_settings_to_configurator(mconfigurator, settings)

        assert mconfigurator.settings == sentinel.settings
        assert mconfigurator.paths == sentinel.paths

    def test_generate_settings(self, plugin, mcreate_settings):
        """
        ._generate_settings should create settings and use all functions
        from .settings_funs on those settings
        """
        mcreate_settings.return_value = {'settings': sentinel.settings}
        fun = MagicMock()
        plugin.settings_funs = [fun]

        assert plugin._generate_settings() == mcreate_settings.return_value

        fun.assert_called_once_with(settings=sentinel.settings)

    def test_gather_settings_for_startpoint(self, plugin, mimport,
                                            mgenerate_settings):
        """
        ._gather_settings_for_startpoint should import settings function depend
        on the startpoint and generate settings from it.
        """
        assert plugin._gather_settings_for_startpoint(
            'startme') == mgenerate_settings.return_value

        assert plugin.settings_funs == []
        mimport.assert_called_once_with(self.MODULE)
        mimport.return_value.startme.assert_called_once_with(plugin)

    def test_append(self, plugin, mimport):
        """
        .append should import settings module and append the startpoin function
        to the .settings_funs
        """
        plugin.settings_funs = []

        plugin.append('somwhere.near', 'myfun')

        mimport.assert_called_once_with('somwhere.near')

        assert plugin.settings_funs == [mimport.return_value.myfun]

    def test_append_when_on_import_error(self, plugin, mimport):
        """
        .append should raise ImportError when the import is wrong.
        """
        mimport.side_effect = ImportError()

        with raises(ImportError):
            plugin.append('wrong')

    def test_append_when_on_import_error_and_silent(self, plugin, mimport):
        """
        .append should not raise error, when the error is sailent.
        """
        mimport.side_effect = ImportError()

        plugin.append('wrong', silent_errors=True)


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
