from abc import ABC


class CustomBaseType:
    pass


class PluginKey(str, CustomBaseType):
    pass


class Application(ABC):
    pass


class Plugin(ABC):
    pass
