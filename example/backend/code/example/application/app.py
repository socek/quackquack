from sapp.plugins.json import JsonPlugin
from sapp.plugins.logging import LoggingPlugin
from sapp.plugins.pyramid.configurator import ConfiguratorWithPyramid
from sapp.plugins.pyramid.plugins import RoutingPlugin
from sapp.plugins.settings import SettingsPlugin

# from sapp.plugins.sqlalchemy.plugin import DatabasePlugin

from example.application.routing import ExampleRouting


class ExampleConfigurator(ConfiguratorWithPyramid):
    def append_plugins(self):
        self.add_plugin(SettingsPlugin("example.application.settings"))
        self.add_plugin(LoggingPlugin())
        self.add_plugin(JsonPlugin())

        # Pyramid
        self.add_plugin(RoutingPlugin(ExampleRouting))

        # self.add_plugin(DatabasePlugin("dbsession"))
