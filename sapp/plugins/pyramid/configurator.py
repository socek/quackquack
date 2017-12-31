from pyramid.config import Configurator as PyramidConfigurator

from sapp.configurator import Configurator


class ConfiguratorWithPyramid(Configurator):
    def start_pyramid_plugins(self, pyramid):
        for plugin in self.plugins:
            method = getattr(plugin, 'start_pyramid', lambda x: x)
            method(pyramid)

    def start_pyramid(self, *args, **kwargs):
        """
        Create application with 'uwsgi' settings and return pyramid's uwsgi
        application object.
        """
        extra = kwargs.pop('extra', {})
        startpoint = kwargs.pop('startpoint', 'pyramid')
        self.start(startpoint, **extra)

        pyramid = PyramidConfigurator(*args, settings=self.settings, **kwargs)
        pyramid.registry['application'] = self
        self.start_pyramid_plugins(pyramid)
        return pyramid.make_wsgi_app()
