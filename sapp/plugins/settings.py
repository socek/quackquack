from os.path import dirname

from sapp.injector import Injector
from sapp.plugin import Plugin


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

    def __init__(self, modulepath: str, name: str = "settings"):
        self.modulepath = modulepath
        self.name = name

    def start(self, configurator):
        self.configurator = configurator
        startpoint = configurator.startpoint or "default"
        startpoints_module = self._import(self.modulepath)
        serttings_fun = getattr(startpoints_module, startpoint)
        self.configurator.extra[self.name] = serttings_fun()

    def enter(self, context):
        print(f"Entering Settings {self.name}|{id(context)}")
        return self.configurator.extra[self.name]

    def exit(self, *args, **kwargs):
        print(f"Exiting Settings")

    def _import(self, modulepath):
        return __import__(modulepath, globals(), locals(), [""])


@Injector
def SettingsInjector(context):
    return context["settings"]
