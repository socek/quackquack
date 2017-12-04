from sapp.application import Application


class ConfiguratorNotStartedError(RuntimeError):
    pass


class ExtraValueMissing(RuntimeError):
    pass


class Configurator(object):
    def __init__(self):
        self.is_started = False
        self.method = None
        self.plugins = []
        self.application_count = 0
        self.application = None

    def start(self, **kwargs):
        self.extra = kwargs

        self.append_plugins()
        self._start_plugins()

        self.is_started = True

    def _start_plugins(self):
        for plugin in self.plugins:
            plugin.start(self)

    def __enter__(self):
        return self.create_application()

    def create_application(self):
        if not self.is_started:
            raise ConfiguratorNotStartedError(
                'Configurator is not started! Use Configurator.start(method)')

        self.application_count += 1
        if not self.application:
            self.application = Application(self)
            self.application.enter()
        return self.application

    def __exit__(self, exc_type, exc_value, traceback):
        self.application_count -= 1
        if self.application_count == 0:
            self.application.exit(exc_type, exc_value, traceback)

    def add_plugin(self, plugin):
        self.plugins.append(plugin)

    def append_plugins(self):
        pass
