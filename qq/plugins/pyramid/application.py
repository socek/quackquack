from pyramid.config import Configurator

from qq.application import Application
from qq.plugins.settings import SettingsPlugin


class PyramidApplication(Application):
    PYRAMID_SETTINGS_KEY = "pyramid"

    def make_wsgi_app(self, *args, **kwargs):
        """
        Configure application for web server and return pyramid's uwsgi
        application object.
        """
        pyramid = Configurator(*args, settings=self.globals[SettingsPlugin.key], **kwargs)
        pyramid.registry["application"] = self
        self._start_pyramid_plugins(pyramid)
        return pyramid.make_wsgi_app()

    def _start_pyramid_plugins(self, pyramid: Configurator):
        for plugin in self.plugins.values():
            method = getattr(plugin, "start_pyramid", lambda x: x)
            method(pyramid)
