from sapp.application import Application


class ConfiguratorNotStartedError(RuntimeError):
    pass


class Configurator(object):
    def __init__(self):
        self.is_started = False
        self.method = None
        self.plugins = []
        self.application_count = 0
        self.application = None

    def start_configurator(self, method):
        self.append_plugins()
        self.init_plugins()

        self.method = method
        self.is_started = True

    def init_plugins(self):
        for plugin in self.plugins:
            plugin.init_plugin(self)

    def __enter__(self):
        return self.create_application()

    def create_application(self):
        if not self.is_started:
            raise ConfiguratorNotStartedError(
                'Configurator is not started! '
                'Use Configurator.start_configurator(method)')

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
