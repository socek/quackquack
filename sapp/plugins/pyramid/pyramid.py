from pyramid.config import Configurator as PyramidConfigurator

from qapla.configurator import Configurator


class ConfiguratorWithPyramid(Configurator):
    def init_web_plugins(self, pyramid):
        for plugin in self.plugins:
            plugin.init_pyramid(pyramid)

    def __call__(self, *args, **kwargs):
        """
        Create application with 'uwsgi' settings and return pyramid's uwsgi
        application object.
        """
        self.start_configurator('uwsgi')

        pyramid = PyramidConfigurator(*args, **kwargs)
        self.init_web_plugins(pyramid)
        return pyramid.make_wsgi_app()
