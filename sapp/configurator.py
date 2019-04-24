from collections import defaultdict
from os import getpid

from sapp.context import Context


class ConfiguratorNotStartedError(RuntimeError):
    pass


class ExtraValueMissing(RuntimeError):
    pass


class FragmentContext(object):
    def __init__(self, configurator, args):
        self.configurator = configurator
        self.args = args

    def __enter__(self):
        ctx = self.configurator.__enter__()
        if len(self.args) == 0:
            return ctx
        elif len(self.args) == 1:
            return getattr(ctx, self.args[0])
        else:
            return [getattr(ctx, arg) for arg in self.args]

    def __exit__(self, *args, **kwargs):
        ctx = self.configurator.__exit__(*args, **kwargs)


class Configurator(object):
    def __init__(self):
        self.is_started = False
        self.startpoint = None
        self.plugins = []
        self.context_count = 0
        self.context = None

    def start(self, startpoint=None, **kwargs):
        self.startpoint = startpoint
        self.extra = kwargs

        self.append_plugins()
        self._start_plugins()

        self.is_started = True

    def _start_plugins(self):
        for plugin in self.plugins:
            plugin.start(self)

    def __enter__(self):
        return self.create_context()

    def create_context(self):
        if not self.is_started:
            raise ConfiguratorNotStartedError(
                "Configurator is not started! Use Configurator.start(startpoint)"
            )

        self.context_count += 1
        if not self.context:
            self.context = Context(self)
            self.context.enter()
        return self.context

    def __exit__(self, exc_type, exc_value, traceback):
        self.context_count -= 1
        if self.context_count == 0:
            self.context.exit(exc_type, exc_value, traceback)

    def add_plugin(self, plugin):
        self.plugins.append(plugin)

    def append_plugins(self):
        pass

    def __call__(self, *args):
        return FragmentContext(self, args)
