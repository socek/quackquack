from pyramid.config import Configurator as PyramidConfigurator

from qapla.application import Application


class Configurator(object):
    def __init__(self):
        self.is_created = False
        self.method = None
        self.plugins = []
        self.application_count = 0
        self.application = None

    def start_configurator(self, method):
        self.method = method

        self.append_plugins()
        self.init_plugins()

        self.is_created = True

    def init_plugins(self):
        for plugin in self.plugins:
            plugin.init_plugin(self)

    def __enter__(self):
        if not self.is_created:
            raise RuntimeError('Configurator is not started! '
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

    def init_pyramid_plugins(self, pyramid):
        for plugin in self.plugins:
            plugin.init_pyramid(pyramid)

    def __call__(self, *args, **kwargs):
        """
        Create application with 'uwsgi' settings and return pyramid's uwsgi
        application object.
        """
        self.start_configurator('uwsgi')

        pyramid = PyramidConfigurator(*args, **kwargs)
        self.init_pyramid_plugins(pyramid)
        return pyramid.make_wsgi_app()

    def append_plugins(self):
        pass
