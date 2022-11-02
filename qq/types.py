from abc import ABC


class BaseInjector:
    pass


class PluginKey(str):
    pass


class Application(ABC):
    pass


class Plugin(ABC):
    pass
