from os.path import dirname

from qq.application import Application
from qq.context import Context
from qq.injector import Injector
from qq.plugin import Plugin

TESTS_KEY = "tests"


def _import(modulepath):
    return __import__(modulepath, globals(), locals(), [""])


class PrefixedStringsDict(dict):
    def __init__(self, prefix="", module=None):
        self.prefix = prefix
        if module:
            self.set_prefix_from_module(module)

    def set_prefix(self, prefix):
        self.prefix = prefix

    def __getitem__(self, key):
        return self.prefix + super().__getitem__(key)

    def __setitem__(self, key, value):
        if not isinstance(value, str):
            raise ValueError("PrefixedStringsDict can be set only by strings!")
        return super().__setitem__(key, value)

    def set_prefix_from_module(self, module):
        self.prefix = dirname(module.__file__)


class SettingsPlugin(Plugin):
    """
    This class will generate settings for different startpoints. `modulepath`
    is a dotted path to the module with the settings startpoints. Startpoint is
    a function which will create proper settings and push them to configurator.
    """

    key = "settings"

    def __init__(self, modulepath: str):
        super().__init__()
        self.modulepath = modulepath
        self._settings = None

    def start(self, application: Application):
        startpoints_module = _import(self.modulepath)
        settings = getattr(startpoints_module, application.startpoint)
        return settings()

    def enter(self, context: Context):
        return context.globals[self.key]


class SettingsBasedPlugin(Plugin):
    def get_my_settings(self, source: (Application, Context)):
        """
        Get settings for this plugin from Application or Context
        """
        return source.globals[SettingsPlugin.key][self.key]


@Injector
def SettingsInjector(context: Context, key: str):
    return context[SettingsPlugin.key][key]
