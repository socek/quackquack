from os.path import dirname

from qq.application import Application
from qq.context import Context
from qq.injector import Injector
from qq.plugin import Plugin


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

    DEFAULT_KEY = "settings"

    def __init__(self, modulepath: str):
        super().__init__()
        self.modulepath = modulepath
        self._settings = None

    def start(self, application: Application):
        startpoints_module = _import(self.modulepath)
        settings = getattr(startpoints_module, application.startpoint)
        self._settings = settings()
        application.extra[self.key] = self._settings

    def enter(self, context: Context):
        return self._settings


@Injector
def SettingsInjector(
    context: Context, settings_key: str = SettingsPlugin.DEFAULT_KEY
):
    return context[settings_key]


class SettingsBasedPlugin(Plugin):
    def __init__(
        self, settings_key: str = SettingsPlugin.DEFAULT_KEY
    ):
        super().__init__()
        self.settings_key = settings_key

    def get_my_settings(
        self, application: Application = None, context: Context = None
    ):
        if application:
            return application.extra[self.settings_key][self.key]
        elif context:
            return context[self.settings_key][self.key]
        else:
            raise TypeError(
                "get_my_settings(application, context) missing 1 required argument: application or context!"
            )
