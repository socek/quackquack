from sapp.context import Context


class ConfiguratorNotStartedError(RuntimeError):
    pass


class ExtraValueMissing(RuntimeError):
    pass


class Configurator:
    def __init__(self):
        self.is_started = False
        self.startpoint = None
        self.plugins = []
        self.context_count = 0
        self.context = None
        self.extra = {}

    def start(self, startpoint: str = None, **kwargs) -> bool:
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
        for plugin in self.plugins:
            plugin.start(self)

    def add_plugin(self, plugin):
        self.plugins.append(plugin)

    def append_plugins(self):
        pass

    def _enter_context(self):
        if not self.is_started:
            raise ConfiguratorNotStartedError(
                "Configurator is not started! Use Configurator.start(startpoint)"
            )
        self.context_count += 1
        if not self.context:
            self.context = Context(self)
            self.context.enter()
        return self.context

    def _exit_context(self, exc_type, exc_value, traceback):
        self.context_count -= 1
        if self.context_count == 0:
            self.context.exit(exc_type, exc_value, traceback)
            self.context = None
