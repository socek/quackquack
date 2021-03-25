from collections import OrderedDict
from contextvars import ContextVar


class AlreadyStartedError(RuntimeError):
    pass


class Application:
    def __init__(self):
        self.is_started = False
        self.startpoint = None
        self.plugins = OrderedDict()
        self.extra = {}
        self.globals = {}
        self.context = ContextVar(self.context_var_key)

    def start(self, startpoint: str = "default", **kwargs) -> bool:
        """
        Start application. Return True if started. Return False if already
        started before.
        """
        if self.is_started:
            raise AlreadyStartedError()

        self.startpoint = startpoint
        self.extra = kwargs

        self.create_plugins()
        self._start_plugins()

        self.is_started = True
        return True

    def _start_plugins(self):
        for key, plugin in self.plugins.items():
            plugin.init(key)
            self.globals[key] = plugin.start(self)

    def create_plugins(self):
        pass

    @property
    def context_var_key(self):
        return f"{self.__class__.__name__}_{id(self)}"
