from example.application.capp import cel
from example.application.routing import ExampleRouting

from qq.plugins.celery.plugin import CeleryPlugin
from qq.plugins.jsonhack import JsonPlugin
from qq.plugins.logging import LoggingPlugin
from qq.plugins.pyramid.configurator import ConfiguratorWithPyramid
from qq.plugins.pyramid.plugins import RoutingPlugin
from qq.plugins.settings import SettingsPlugin
from qq.plugins.sqlalchemy.plugin import DatabasePlugin
from qq.plugins.tornado.configurator import TornadoConfigurator
from qq.plugins.tornado.plugin import TornadoPlugin


class ExampleConfigurator(ConfiguratorWithPyramid, TornadoConfigurator):
    def create_plugins(self):
        self.add_plugin(SettingsPlugin("example.application.settings"))
        self.add_plugin(LoggingPlugin())
        self.add_plugin(JsonPlugin())

        self.add_plugin(RoutingPlugin(ExampleRouting))
        self.add_plugin(DatabasePlugin("dbsession"))
        self.add_plugin(CeleryPlugin(cel))
        self.add_plugin(TornadoPlugin())
