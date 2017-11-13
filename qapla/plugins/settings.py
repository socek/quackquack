from qapla.plugin import Plugin
from qapla.settings import SettingsFactory


class SettingsPlugin(Plugin):
    def __init__(self, settings_module, settings_factory=SettingsFactory):
        self.settings_module = settings_module
        self.settings_factory = settings_factory

    def start_plugin(self, configurator):
        method = configurator.method
        factory = self.settings_factory(self.settings_module)
        self.settings, self.paths = factory.get_for(method)

        configurator.settings = self.settings
        configurator.paths = self.paths

    def start_web_plugin(self, pyramid):
        pyramid.registry['settings'] = self.settings
        pyramid.registry['paths'] = self.paths

    def enter(self, application):
        application.settings = self.settings
        application.paths = self.paths
