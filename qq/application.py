from contextvars import ContextVar

from qq.errors import AlreadyStartedError
from qq.plugin_container import PluginContainer
from qq.types import Application as ApplicationType

KEY_PREFIX = "quackquack"


class Application(ApplicationType):
    def __init__(self):
        self.is_started = False
        self.startpoint = None
        self.plugins = PluginContainer()
        self.extra = {}
        self.globals = {}
        self.context = ContextVar(self.context_var_key)

    def start(self, startpoint: str = "default", **kwargs):
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

    def _start_plugins(self):
        for key, plugin in self.plugins.items():
            plugin.init(key)
            self.globals[key] = plugin.start(self)

    def create_plugins(self):
        pass

    @property
    def context_var_key(self):
        return f"{KEY_PREFIX}_{self.__class__.__name__}"
