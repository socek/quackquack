from pyramid.config import Configurator as PyramidConfigurator

from sapp.configurator import Configurator


class ConfiguratorWithPyramid(Configurator):
    def make_wsgi_object(self, *args, **kwargs):
        """
        Configure application for web server and return pyramid's uwsgi
        application object.
        """
        pyramid = PyramidConfigurator(*args, settings=self.settings, **kwargs)
        pyramid.registry['application'] = self
        self._start_pyramid_plugins(pyramid)
        return pyramid.make_wsgi_app()

    def _start_pyramid_plugins(self, pyramid):
        for plugin in self.plugins:
            method = getattr(plugin, 'start_pyramid', lambda x: x)
            method(pyramid)
