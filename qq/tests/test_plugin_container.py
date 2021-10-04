from unittest.mock import MagicMock

from pytest import fixture
from pytest import raises

from qq.errors import PluginKeyAlreadyDefinedError
from qq.errors import PluginLacksOfKeyError
from qq.errors import WrongKeyForPluginError
from qq.plugin_container import PluginContainer


class TestPluginContainer:
    @fixture
    def container(self):
        return PluginContainer()

    @fixture
    def plugin(self):
        return MagicMock(key=None)

    @fixture
    def singleton_plugin(self):
        return MagicMock(key="plugin")

    def test_calling_not_singleton_plugin(self, container, plugin):
        """
        PluginContainer should raise PluginLacksOfKeyError when plugin has no
        global .key parameter.
        """
        with raises(PluginLacksOfKeyError):
            container(plugin)

    def test_calling_singleton_plugin(self, container, singleton_plugin):
        """
        PluginContainer should accept calling plugin with global .key parameter
        defined.
        """
        container(singleton_plugin)

        assert container[singleton_plugin.key] == singleton_plugin

    def test_settings_singleton_plugin_with_wrong_key(
        self, container, singleton_plugin
    ):
        """
        PluginContainer should raise WrongKeyForPluginError when trying to set
        singleton plugin with key which is not equal to Plugin's .key parameter.
        """
        with raises(WrongKeyForPluginError):
            container["wron_name"] = singleton_plugin

    def test_settings_plugin_which_is_already_there(self, container, plugin):
        """
        PluginContainer should raise PluginKeyAlreadyDefinedError when trying
        to set plugin to a key that is already there.
        """
        container["key"] = plugin
        with raises(PluginKeyAlreadyDefinedError):
            container["key"] = plugin

    def test_setting_plugin(self, container, plugin):
        """
        PluginContainer should set the plugin to a provided key.
        """
        container["key"] = plugin
        assert container["key"] == plugin

    def test_setting_singleton_plugin(self, container, singleton_plugin):
        """
        PluginContainer should set the singleton plugin to a provided key if it
        matches the plugin's .key parameter.
        """
        container[singleton_plugin.key] = singleton_plugin
        assert container[singleton_plugin.key] == singleton_plugin
