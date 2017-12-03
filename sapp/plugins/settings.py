from collections import namedtuple

from morfdict import Factory

from sapp.plugin import Plugin

SettingsModule = namedtuple('SettingsModule', ['name', 'is_needed'])


class SettingsPlugin(Plugin):
    """
    This class will generate settings for different endpoints. settings_module
    is a dotted prefix for the settings (for example app.settings). All
    endpoints will import the default module. After that the endpoint will try
    to import the rest modules provided in the list. If it is with `True`, the
    Factory will raise an error (FileNotFound). Otherwise the error will not be
    raised.
    """

    METHODS = {
        'pyramid': [
            SettingsModule('pyramid', False),
            SettingsModule('local', False)],
        'tests': [
            SettingsModule('tests', False),
            SettingsModule('local', False)],
        'shell': [
            SettingsModule('shell', False),
            SettingsModule('local', False)],
        'command': [
            SettingsModule('command', False),
            SettingsModule('local', False)],
    }

    def __init__(self, settings_module):
        self.settings_module = settings_module

    def start_plugin(self, configurator):
        self._start_for_method(configurator.method)

        configurator.settings = self.settings
        configurator.paths = self.paths

    def enter(self, application):
        application.settings = self.settings
        application.paths = self.paths

    def _start_for_method(self, endpoint):
        files = self.METHODS[endpoint]
        factory = Factory(self.settings_module)
        self.settings, self.paths = factory.make_settings(
            settings={},
            additional_modules=files,
        )
