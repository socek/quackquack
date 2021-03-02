from collections import OrderedDict
from contextvars import ContextVar

from qq.plugin import Plugin


class Application:
    def __init__(self):
        self.is_started = False
        self.startpoint = None
        self.plugins = OrderedDict()
        self.extra = {}
        self.context = ContextVar(self.context_var_key())

    def context_var_key(self):
        return f"{self.__class__.__name__}_{id(self)}"

    def start(self, startpoint: str = "default", **kwargs) -> bool:
        """
        Start application. Return True if started. Return False if already
        started before.
        """
        if self.is_started:
            return False
        self.startpoint = startpoint
        self.extra = kwargs

        self.append_plugins()
        self._start_plugins()

        self.is_started = True
        return True

    def _start_plugins(self):
        for plugin in self.plugins.values():
            result = plugin.start(self)
            self.extra[plugin.key] = result

    def add_plugin(self, plugin: Plugin):
        self.plugins[plugin.key] = plugin

    def append_plugins(self):
        pass
