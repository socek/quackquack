from pyramid.config import Configurator as PyramidConfigurator

from sapp.configurator import Configurator


class ConfiguratorWithPyramid(Configurator):
    def start_pyramid(self, pyramid):
        for plugin in self.plugins:
            method = getattr(plugin, 'start_pyramid', lambda x: x)
            method(pyramid)

    def __call__(self, *args, **kwargs):
        """
        Create application with 'uwsgi' settings and return pyramid's uwsgi
        application object.
        """
        self.start_configurator('wsgi')

        pyramid = PyramidConfigurator(*args, **kwargs)
        self.start_pyramid(pyramid)
        return pyramid.make_wsgi_app()
