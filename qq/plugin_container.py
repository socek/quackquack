from collections import OrderedDict

from qq.errors import PluginKeyAlreadyDefinedError
from qq.errors import PluginLacksOfKeyError
from qq.errors import WrongKeyForPluginError
from qq.types import Plugin
from qq.types import PluginKey


class PluginContainer(OrderedDict):
    def __call__(self, plugin: Plugin):
        if not plugin.key:
            raise PluginLacksOfKeyError()
        self[plugin.key] = plugin

    def __setitem__(self, key: PluginKey, plugin: Plugin):
        if plugin.key and plugin.key != key:
            raise WrongKeyForPluginError()
        if key in self:
            raise PluginKeyAlreadyDefinedError()
        super().__setitem__(key, plugin)
