import os
from os.path import dirname
from unittest.mock import MagicMock
from unittest.mock import patch
from unittest.mock import sentinel

from pytest import fixture
from pytest import raises

from qq.plugins.settings import PrefixedStringsDict
from qq.plugins.settings import SettingsPlugin
from qq.plugins.settings import _import
from qq.testing import PluginFixtures

PREFIX = "qq.plugins.settings"


class TestSettingsPlugin(PluginFixtures):
    MODULE = sentinel.settings_module

    @fixture
    def plugin(self):
        plugin = SettingsPlugin(self.MODULE)
        plugin._set_key("settings")
        return plugin

    @fixture
    def mstring_dict(self):
        return {}

    @fixture
    def mpaths(self):
        with patch(f"{PREFIX}.PrefixedStringsDict") as mock:
            yield mock

    @fixture
    def mapp(self):
        return MagicMock()

    @fixture
    def mimport(self):
        with patch(f"{PREFIX}._import") as mock:
            yield mock

    def test_application(self, plugin, mapplication, mapp):
        """
        .enter should add settings and paths to the application.
        """
        plugin._settings = {"settings": sentinel.settings}
        assert plugin.enter(None) == {"settings": sentinel.settings}

    def test_import(self, plugin):
        assert _import("os") == os

    def test_start(self, plugin, mapp, mimport):
        """
        .start should gather settings for startpoint and push the data into
        configurator.
        """
        mapp.startpoint = "myapp"
        mapp.extra = {}

        plugin.start(mapp)

        mimport.assert_called_once_with(self.MODULE)
        mimport.return_value.myapp.assert_called_once_with()

        assert mapp.extra["settings"] == mimport.return_value.myapp.return_value


class TestPrefixedStringsDict:
    @fixture
    def paths(self):
        return PrefixedStringsDict()

    def test_set_prefix(self, paths):
        """
        .set_prefix should set prefix on the paths.
        """
        paths["name"] = "come"
        assert paths["name"] == "come"

        paths.set_prefix("myprefix/")
        assert paths["name"] == "myprefix/come"

    def test_setitem_with_bad_value(self, paths):
        """
        PrefixedStringsDict can be set only by the str objects.
        """
        paths["name"] = "key"

        with raises(ValueError):
            paths["name"] = 12

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
